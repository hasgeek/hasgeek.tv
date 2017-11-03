<template>
  <div class="content-head mui--hidden-xs mui--hidden-sm">
    <div class="mui-container">
      <div class="grid grid--align-baseline">
        <div class="grid__col-xs-12">
          <h3 class="mui--text-title content-head__title">
            <a :href="channel.url">{{ channel.title }}</a> <i class="material-icons mui--align-middle mui--text-hyperlink mui--text-title">chevron_right</i>
            <a :href="playlist.url">{{ playlist.title }}</a>
          </h3>
          <p class="mui--text-headline content-head__title">{{ video.title }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoHeader',
  props: ['channel', 'playlist', 'video'],
};
</script>

<style scoped>
</style>
