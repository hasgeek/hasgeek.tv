<template>
  <div>
    <ChannelHeader :channel="channel"></ChannelHeader>
    <Playlists :channel="channel" :playlists="playlists"></Playlists>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import Utils from '../assets/js/utils';

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
    ChannelHeader: () => import('./ChannelHeader.vue'),
    Playlists: () => import('./Playlists.vue'),
    DisplayError: () => import('./DisplayError.vue'),
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.channel = response.data.channel;
      this.playlists = response.data.playlists;
    },
    onErrorJsonFetch(error) {
      this.error = error;
    },
  },
  created() {
    Utils.fetchJson.bind(this)();
  },
};
</script>

<style scoped>
</style>
