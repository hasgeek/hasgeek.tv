<template>
  <div class="mui-container">
    <div class="page-content">
      <div class="grid">
        <div v-for="playlist in playlists" class="grid grid--align-baseline playlist">
          <div class="grid__col-xs-12 grid__col-sm-8">
            <h3 class="mui--text-headline">{{ playlist.title }}</h3>
          </div>
          <div class="grid__col-sm-4">
            <router-link :to="{ name: 'Playlist', params: { channel: channel.name, playlist: playlist.name }}" class="mui--text-body2 playlist-link">
              <span v-if="playlist.videos">VIEW ALL TALKS</span>
              <span v-else>VIEW PLAYLIST</span>
            </router-link>
          </div>
          <div v-else class="mui--hidden-xs grid__col-xs-12">
            <p class="mui--text-body2">This channel does not have any playlists.</p>
          </div>
          <div v-for="video in playlist.videos" class="grid__col-auto thumbnail-wrapper">
            <router-link :to="{ name: 'Video', params: { channel: channel.name, playlist: playlist.name, video: video.url_name }}" class="thumbnail thumbnail--video" v-if="video.thumbnail">
              <img :src="video.thumbnail" class="img-responsive"/>
              <div class="overlay"></div>
              <i class="material-icons thumbnail__play-icon">play_circle_outline</i>
            </router-link>
            <p class="mui--text-body1">{{ video.title }}</p>
          </div>
          <div v-else class="mui--visible-xs-block grid__col-xs-12">
            <p class="mui--text-body2">This channel does not have any playlists.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'Playlists',
  props: ['channel', 'playlists'],
};
</script>

<style scoped>
</style>
