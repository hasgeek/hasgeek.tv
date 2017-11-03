<template>
  <div>
    <ChannelHeader :channel="channel"></ChannelHeader>
    <Playlists :playlists="playlists"></Playlists>
  </div>
</template>

<script>
import axios from 'axios';
import ChannelHeader from '@/components/ChannelHeader';
import Playlists from '@/components/Playlists';

export default {
  name: 'Channel',
  data() {
    return {
      channel: {},
      playlists: [],
      path: this.$route.path,
      errors: [],
    };
  },
  components: {
    ChannelHeader,
    Playlists,
  },
  created() {
    axios.get(this.path)
    .then((response) => {
      this.channel = response.data.channel;
      this.playlists = response.data.playlists;
    })
    .catch((e) => {
      this.errors.push(e);
    });
  },
};
</script>

<style scoped>
</style>
