<template>
  <div class="content-head mui--hidden-xs mui--hidden-sm">
    <div class="mui-container">
      <div class="grid grid--align-baseline">
        <div class="grid__col-xs-12">
          <h3 class="mui--text-headline content-head__title">
            <router-link :to="{ name: 'Channel', params: { channel: channel.name }}">{{ channel.title }}</router-link> <i class="material-icons mui--align-middle mui--text-hyperlink mui--text-title">chevron_right</i> <router-link :to="{ name: 'Playlist', params: { channel: channel.name, playlist: playlist.name }}">{{ playlist.title }}</router-link>
          </h3>
          <p class="mui--text-subhead content-head__title">{{ video.title }}</p>
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
