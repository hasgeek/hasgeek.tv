<template>
  <div>
    <VideoHeader :channel="channel" :playlist="playlist" :video="video"></VideoHeader>
    <a v-if="playlist.banner_ad_url" :href="playlist.banner_ad_url" class="sponsor-bannerimg" target="_blank"><img :src="playlist.banner_ad_filename" class="card__image"/></a>
    <VideoPlayer :user="user"  :channel="channel" :playlist="playlist" :video="video" :speakers="speakers" :relatedVideos="relatedVideos" @update="flagsUpdate"></VideoPlayer>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import Utils from '../assets/js/utils';

export default {
  name: 'Video',
  data() {
    return {
      channel: {},
      playlist: {},
      video: [],
      speakers: [],
      relatedVideos: [],
      user: {},
      errors: [],
    };
  },
  components: {
    VideoHeader: () => import('./VideoHeader.vue'),
    VideoPlayer: () => import('./VideoPlayer.vue'),
    DisplayError: () => import('./DisplayError.vue'),
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData',
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.channel = response.data.channel;
      this.playlist = response.data.playlist;
      this.video = response.data.video;
      this.speakers = response.data.speakers;
      this.relatedVideos = response.data.relatedVideos;
      this.user = response.data.user;
      Utils.setPageTitle(this.video.title, this.playlist.title);
    },
    onErrorJsonFetch(error) {
      this.error = error;
    },
    flagsUpdate(data) {
      this.user.flags = data;
    },
    fetchData() {
      this.$NProgress.configure({ showSpinner: false }).start();
      Utils.fetchJson.bind(this)();
    },
  },
  created() {
    this.fetchData();
  },
};
</script>

<style scoped>
</style>
