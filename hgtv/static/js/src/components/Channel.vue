<template>
  <div>
    <ChannelHeader :channel="channel"></ChannelHeader>
    <Playlists :channel="channel" :playlists="playlists"></Playlists>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import axios from 'axios';
import ChannelHeader from '@/components/ChannelHeader';
import Playlists from '@/components/Playlists';
import DisplayError from '@/components/DisplayError';

export default {
  name: 'Channel',
  data() {
    return {
      channel: {},
      playlists: [],
      path: this.$route.path,
      error: '',
    };
  },
  components: {
    ChannelHeader,
    Playlists,
    DisplayError,
  },
  created() {
    axios.get(this.path)
    .then((response) => {
      this.channel = response.data.channel;
      this.playlists = response.data.playlists;
    })
    .catch((error) => {
      this.error = error;
    });
  },
};
</script>

<style scoped>
</style>
