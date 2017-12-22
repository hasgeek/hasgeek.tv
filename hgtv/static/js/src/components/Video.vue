<template>
  <div>
    <VideoHeader :channel="channel" :playlist="playlist" :video="video"></VideoHeader>
    <a v-if="playlist.banner_ad_url" :href="playlist.banner_ad_url" class="sponsor-bannerimg" target="_blank"><img :src="playlist.banner_ad_filename" class="card__image"/></a>
    <VideoPlayer :user="user"  :channel="channel" :playlist="playlist" :video="video" :speakers="speakers" :relatedVideos="relatedVideos" :path="path" @update="flagsUpdate"></VideoPlayer>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import axios from 'axios';
import VideoHeader from '@/components/VideoHeader';
import VideoPlayer from '@/components/VideoPlayer';
import DisplayError from '@/components/DisplayError';

export default {
  name: 'Video',
  data() {
    return {
      channel: {},
      playlist: {},
      video: [],
      speakers: [],
      relatedVideos: [],
      path: this.$route.path,
      user: {},
      errors: [],
    };
  },
  components: {
    VideoHeader,
    VideoPlayer,
    DisplayError,
  },
  methods: {
    flagsUpdate(data) {
      this.user.flags = data;
    },
  },
  created() {
    axios.get(this.path)
    .then((response) => {
      this.channel = response.data.channel;
      this.playlist = response.data.playlist;
      this.video = response.data.video;
      this.speakers = response.data.speakers;
      this.relatedVideos = response.data.relatedVideos;
      this.user = response.data.user;
    })
    .catch((error) => {
      this.error = error;
    });
  },
};
</script>

<style scoped>
</style>
