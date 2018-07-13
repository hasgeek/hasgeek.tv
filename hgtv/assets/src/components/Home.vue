<template>
  <div>
    <HomeBanner></HomeBanner>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <p class="grid__col-12 site-title">Welcome to HasGeek TV. Watch talks and discussions from past events here.</p>
          <LiveStream v-if="livestreamOn" :livestreams="livestreams"></LiveStream>
        </div>
        <FeaturedChannels :channels="channels"></FeaturedChannels>
      </div>
    </div>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import Utils from '../assets/js/utils';

export default {
  name: 'Home',
  data() {
    return {
      channels: [],
      path: this.$route.path,
      livestreamOn: false,
      livestreams: [],
      errors: [],
    };
  },
  components: {
    HomeBanner: () => import('./HomeBanner.vue'),
    LiveStream: () => import('./LiveStream.vue'),
    FeaturedChannels: () => import('./FeaturedChannels.vue'),
    DisplayError: () => import('./DisplayError.vue'),
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.channels = response.data.channels;
      this.livestreamOn = response.data.livestream.enable;
      this.livestreams = response.data.livestream.streams;
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
