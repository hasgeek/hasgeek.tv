<template>
  <div class="site-banner">
    <picture>
      <source media="(max-width: 768px)" srcset="@/assets/img/banner-mobile.png" :alt="title" class="site-banner__img site-banner__img--mobile">
      <source srcset="@/assets/img/banner-desktop.png" :alt="title" class="site-banner__img">
      <img src="@/assets/img/banner-mobile.png" :alt="title" class="site-banner__img">
    </picture>
    <h2 class="site-banner__title">1200 videos, 52 events and counting...</h2>
  </div>
</template>

<script>
export default {
  name: 'HomeBanner',
  data() {
    return {
      title: window.hgtv.siteTitle,
    };
  },
};
</script>

<style scoped>
</style>
