<template>
  <div>
    <PlaylistHeader :channel="channel" :playlist="playlist"></PlaylistHeader>
    <a v-if="playlist.banner_ad_url" :href="playlist.banner_ad_url" class="sponsor-bannerimg" target="_blank"><img :src="playlist.banner_ad_filename" class="card__image"/></a>
    <Videos :playlist="playlist" :videos="videos"></Videos>
  </div>
</template>

<script>
import axios from 'axios';
import PlaylistHeader from '@/components/PlaylistHeader';
import Videos from '@/components/Videos';

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
    PlaylistHeader,
    Videos,
  },
  created() {
    axios.get(this.path)
    .then((response) => {
      this.channel = response.data.channel;
      this.playlist = response.data.playlist;
      this.videos = response.data.playlist.videos;
    })
    .catch((e) => {
      this.errors.push(e);
    });
  },
};
</script>

<style scoped>
</style>
