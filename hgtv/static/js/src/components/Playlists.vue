<template>
  <div class="mui-container">
    <div class="page-content">
      <div class="grid">
        <div v-for="playlist in playlists" class="grid grid--align-baseline playlist">
          <div class="grid__col-xs-12 grid__col-sm-8">
            <h3 class="mui--text-headline">{{ playlist.title }}</h3>
          </div>
          <div v-if="playlist.videos" class="mui--hidden-xs grid__col-sm-4">
            <a :href="playlist.url" class="mui--text-body2 playlist-link">VIEW ALL TALKS</a>
          </div>
          <div v-else class="mui--hidden-xs grid__col-xs-12">
            <p class="mui--text-body2">This channel does not have any playlists.</p>
          </div>
          <div v-for="video in playlist.videos" class="grid__col-auto thumbnail-wrapper">
            <a :href="video.url" class="thumbnail thumbnail--video" v-if="video.thumbnail">
              <img :src="video.thumbnail" class="img-responsive"/>
              <div class="overlay"></div>
             <i class="material-icons thumbnail__play-icon">play_circle_outline</i>
            </a>
            <p class="mui--text-body1">{{ video.title }}</p>
          </div>
          <div v-if="playlist.videos" class="grid__col-xs-12 mui--visible-xs-block mui--text-right">
            <a :href="playlist.url" class="mui--text-body2 playlist-link">VIEW ALL TALKS</a>
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
  props: ['playlists'],
};
</script>

<style scoped>
</style>
