<template>
  <div class="channels">
    <HomeBanner></HomeBanner>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <p class="grid__col-12 site-title">Welcome to HasGeek TV. Watch talks and discussions from past events here.</p>
          <LiveStream v-if="livestreamOn" v-bind:livestreams="livestreams"></LiveStream>
        </div>
        <FeaturedChannels v-bind:channels="channels"></FeaturedChannels>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import HomeBanner from '@/components/HomeBanner';
import LiveStream from '@/components/LiveStream';
import FeaturedChannels from '@/components/FeaturedChannels';

export default {
  name: 'Home',
  data() {
    return {
      channels: [],
      path: this.$route.path,
      livestreamOn: false,
      livestreams: [],
    };
  },
  components: {
    HomeBanner,
    LiveStream,
    FeaturedChannels,
  },
  created() {
    axios.get(this.path)
    .then((response) => {
      this.channels = response.data.channels;
      this.livestreamOn = response.data.livestream.enable;
      this.livestreams = response.data.livestream.streams;
    })
    .catch((e) => {
      this.errors.push(e);
    });
  },
};
</script>

<style lang="css">
@import '../assets/css/tabs-component.css';
</style>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
