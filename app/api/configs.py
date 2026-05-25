from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..db import get_session
from ..models import Config, Leg
from ..schemas import ConfigOut, ConfigPayload, LegPayload

router = APIRouter(prefix="/api/configs", tags=["configs"])


def _validate_payload(p: ConfigPayload) -> None:
    if not p.legs:
        raise HTTPException(status_code=400, detail="config must have at least one leg")
    today = date.today()
    for leg in p.legs:
        if not leg.origins:
            raise HTTPException(status_code=400, detail=f"leg {leg.ordinal}: origins empty")
        if not leg.destinations:
            raise HTTPException(status_code=400, detail=f"leg {leg.ordinal}: destinations empty")
        try:
            anchor = datetime.strptime(leg.date_anchor, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"leg {leg.ordinal}: bad date_anchor")
        if anchor < today:
            raise HTTPException(status_code=400, detail=f"leg {leg.ordinal}: date_anchor in the past")
    if not p.structures:
        raise HTTPException(status_code=400, detail="must price at least one structure")
    if p.passengers.get("adults", 0) < 1:
        raise HTTPException(status_code=400, detail="must have at least 1 adult")


def _to_out(cfg: Config, legs: list[Leg]) -> ConfigOut:
    from ..preferences import CostAssumptions, Preferences

    return ConfigOut(
        id=cfg.id,
        name=cfg.name,
        budget_party_total=cfg.budget_party_total,
        currency=cfg.currency,
        passengers=cfg.passengers,
        structures=cfg.structures,
        blackout_ranges=cfg.blackout_ranges,
        validation_tolerance_pct=cfg.validation_tolerance_pct,
        validation_top_n=cfg.validation_top_n,
        envelope_long_gap_days=cfg.envelope_long_gap_days,
        preferences=Preferences.model_validate(cfg.preferences or {}),
        cost_assumptions=CostAssumptions.model_validate(cfg.cost_assumptions or {}),
        legs=[LegPayload.model_validate(l) for l in sorted(legs, key=lambda x: x.ordinal)],
        created_at=cfg.created_at,
        updated_at=cfg.updated_at,
    )


@router.get("", response_model=list[ConfigOut])
def list_configs():
    with get_session() as session:
        cfgs = session.scalars(select(Config).order_by(Config.id)).all()
        out = []
        for c in cfgs:
            legs = session.scalars(select(Leg).where(Leg.config_id == c.id)).all()
            out.append(_to_out(c, list(legs)))
        return out


@router.post("", response_model=ConfigOut, status_code=201)
def create_config(payload: ConfigPayload):
    _validate_payload(payload)
    with get_session() as session:
        cfg = Config(
            name=payload.name,
            budget_party_total=payload.budget_party_total,
            currency=payload.currency,
            passengers=payload.passengers,
            structures=payload.structures,
            blackout_ranges=payload.blackout_ranges,
            validation_tolerance_pct=payload.validation_tolerance_pct,
            validation_top_n=payload.validation_top_n,
            envelope_long_gap_days=payload.envelope_long_gap_days,
            preferences=payload.preferences.model_dump(mode="json"),
            cost_assumptions=payload.cost_assumptions.model_dump(mode="json"),
        )
        session.add(cfg)
        session.commit()
        session.refresh(cfg)
        for leg_p in payload.legs:
            session.add(Leg(
                config_id=cfg.id,
                ordinal=leg_p.ordinal,
                origins=leg_p.origins,
                destinations=leg_p.destinations,
                date_anchor=leg_p.date_anchor,
                window_days=leg_p.window_days,
                sampling_strategy=leg_p.sampling_strategy,
                return_date_anchor=leg_p.return_date_anchor,
                return_window_days=leg_p.return_window_days,
                return_sampling_strategy=leg_p.return_sampling_strategy,
            ))
        session.commit()
        legs = session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all()
        return _to_out(cfg, list(legs))


@router.get("/{config_id}", response_model=ConfigOut)
def get_config(config_id: int):
    with get_session() as session:
        cfg = session.get(Config, config_id)
        if cfg is None:
            raise HTTPException(404, "config not found")
        legs = session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all()
        return _to_out(cfg, list(legs))


@router.put("/{config_id}", response_model=ConfigOut)
def update_config(config_id: int, payload: ConfigPayload):
    _validate_payload(payload)
    with get_session() as session:
        cfg = session.get(Config, config_id)
        if cfg is None:
            raise HTTPException(404, "config not found")
        cfg.name = payload.name
        cfg.budget_party_total = payload.budget_party_total
        cfg.currency = payload.currency
        cfg.passengers = payload.passengers
        cfg.structures = payload.structures
        cfg.blackout_ranges = payload.blackout_ranges
        cfg.validation_tolerance_pct = payload.validation_tolerance_pct
        cfg.validation_top_n = payload.validation_top_n
        cfg.envelope_long_gap_days = payload.envelope_long_gap_days
        cfg.preferences = payload.preferences.model_dump(mode="json")
        cfg.cost_assumptions = payload.cost_assumptions.model_dump(mode="json")
        cfg.updated_at = datetime.now(timezone.utc)
        session.add(cfg)
        # Replace legs wholesale
        existing = session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all()
        for l in existing:
            session.delete(l)
        for leg_p in payload.legs:
            session.add(Leg(
                config_id=cfg.id,
                ordinal=leg_p.ordinal,
                origins=leg_p.origins,
                destinations=leg_p.destinations,
                date_anchor=leg_p.date_anchor,
                window_days=leg_p.window_days,
                sampling_strategy=leg_p.sampling_strategy,
                return_date_anchor=leg_p.return_date_anchor,
                return_window_days=leg_p.return_window_days,
                return_sampling_strategy=leg_p.return_sampling_strategy,
            ))
        session.commit()
        legs = session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all()
        return _to_out(cfg, list(legs))


@router.get("/{config_id}/preview")
def preview_config(config_id: int):
    """Dry-run preview: how the orchestrator will expand the matrix under the
    current preferences. Lets the operator see SerpAPI cost + constructed
    stopover count BEFORE committing.

    Returns: matrix_size (total fare queries), planned_serpapi_calls (floor
    estimate — validation top-N × legs), constructed_stopover_count.
    """
    from ..orchestrator.matrix import LegSpec, expand_leg
    from ..orchestrator.stopover import construct_stopover_itineraries
    from ..preferences import Axis, Preferences, ScalePosition

    with get_session() as session:
        cfg = session.get(Config, config_id)
        if cfg is None:
            raise HTTPException(404, "config not found")
        legs = list(session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all())
        try:
            prefs = Preferences.model_validate(cfg.preferences or {})
        except Exception as e:  # noqa: BLE001
            raise HTTPException(422, f"invalid preferences: {e}") from e

        pax = cfg.passengers or {}
        adults = int(pax.get("adults", 1))
        base_specs = [
            LegSpec(
                ordinal=l.ordinal, origins=l.origins, destinations=l.destinations,
                date_anchor=l.date_anchor, window_days=l.window_days,
                sampling_strategy=l.sampling_strategy,
                return_date_anchor=l.return_date_anchor,
                return_window_days=l.return_window_days,
                return_sampling_strategy=l.return_sampling_strategy,
            )
            for l in sorted(legs, key=lambda x: x.ordinal)
        ]
        base_matrix = sum(len(expand_leg(s, adults=adults)) for s in base_specs)

        stopover_default = prefs.defaults.get(Axis.STOPOVER)
        stopover_count = 0
        stopover_matrix = 0
        if (
            stopover_default is not None
            and stopover_default.position == ScalePosition.HARD_YES
            and prefs.stopover_target is not None
        ):
            svs = construct_stopover_itineraries(
                base_legs=base_specs, stopover_target=prefs.stopover_target,
            )
            stopover_count = len(svs)
            for sv in svs:
                stopover_matrix += sum(len(expand_leg(s, adults=adults)) for s in sv.legs)

        # SerpAPI floor: validation top_n × per-structure leg count.
        per_struct = {"A": 3, "B": 2}
        planned_serpapi_calls = cfg.validation_top_n * sum(
            per_struct.get(s, len(legs)) for s in (cfg.structures or [])
        )

        return {
            "matrix_size": base_matrix + stopover_matrix,
            "base_matrix_size": base_matrix,
            "stopover_matrix_size": stopover_matrix,
            "constructed_stopover_count": stopover_count,
            "planned_serpapi_calls": planned_serpapi_calls,
            "would_filter_count_by_axis": {},  # populated only after a real run
        }


@router.delete("/{config_id}", status_code=204)
def delete_config(config_id: int):
    with get_session() as session:
        cfg = session.get(Config, config_id)
        if cfg is None:
            raise HTTPException(404, "config not found")
        for l in session.scalars(select(Leg).where(Leg.config_id == cfg.id)).all():
            session.delete(l)
        session.delete(cfg)
        session.commit()
