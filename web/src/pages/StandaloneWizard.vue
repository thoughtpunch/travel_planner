<script setup lang="ts">
import { useRouter } from "vue-router";
import Message from "primevue/message";
const router = useRouter();
</script>

<template>
  <Message severity="info" :closable="false">
    Wizards live inside a trip workspace. <a href="#" @click.prevent="router.push('/')">Pick or create a trip from the dashboard</a>.
  </Message>
</template>
