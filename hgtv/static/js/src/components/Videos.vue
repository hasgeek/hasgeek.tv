<template>
  <div class="mui-container">
    <div class="page-content">
      <div v-if="playlist.description" class="grid">
        <div class="grid__col-xs-12 ">
          <div v-html="playlist.description" class="panel"></div>
        </div>
      </div>
      <div v-else class="clearline"></div>
      <div class="grid playlist">
        <div v-if="videos" v-for="video in videos" class="grid__col-12 grid__col-xs-12 grid__col-sm-4 grid__col-lg-3 thumbnail-wrapper thumbnail-wrapper--margin">
          <router-link :to="{ name: 'Video', params: { channel: channel.name, playlist: playlist.name, video:video.url }}" class="thumbnail thumbnail--video" v-if="video.thumbnail">
            <img :src="video.thumbnail" class="img-responsive"/>
            <div class="overlay"></div>
            <i class="material-icons thumbnail__play-icon">play_circle_outline</i>
          </router-link>
          <p class="mui--text-body1">{{ video.title }}</p>
          <span v-for="speaker in video.speakers" class="mui--text-body1">
            <i class="material-icons mui--text-subhead mui--align-top">person</i> {{ speaker }}
          </span>
        </div>
        <div v-else class="grid__col-12">
          <p class="mui--text-body2">This playlist has no videos</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Videos',
  props: ['channel', 'playlist', 'videos'],
};
</script>

<style scoped>
</style>
