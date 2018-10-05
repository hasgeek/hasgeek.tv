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
      Utils.setPageTitle(this.channel.title);
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
