<script setup>
import { RouterView, useRoute } from 'vue-router'

const route = useRoute()

</script>

<template>
  <div>
    <router-view v-slot="{ Component }">
      <transition>
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<style></style>
