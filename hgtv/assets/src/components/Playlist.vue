<template>
  <div>
    <PlaylistHeader :channel="channel" :playlist="playlist"></PlaylistHeader>
    <a v-if="playlist.banner_ad_url" :href="playlist.banner_ad_url" class="sponsor-bannerimg" target="_blank"><img :src="playlist.banner_ad_filename" class="card__image"/></a>
    <Videos :channel="channel" :playlist="playlist" :videos="videos" wait-for="data-loaded"></Videos>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import Utils from '../assets/js/utils';

export default {
  name: 'Playlist',
  data() {
    return {
      channel: {},
      playlist: {},
      videos: [],
      path: this.$route.path,
      errors: [],
    };
  },
  components: {
    PlaylistHeader: () => import('./PlaylistHeader.vue'),
    Videos: () => import('./Videos.vue'),
    DisplayError: () => import('./DisplayError.vue'),
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.channel = response.data.channel;
      this.playlist = response.data.playlist;
      this.videos = response.data.playlist.videos;
      this.$emit('data-loaded');
      Utils.setPageTitle(this.playlist.title);
    },
    onErrorJsonFetch(error) {
      this.error = error;
    },
  },
  beforeCreate() {
    this.$NProgress.configure({ showSpinner: false }).start();
  },
  created() {
    Utils.fetchJson.bind(this)();
  },
};
</script>

<style scoped>
</style>
