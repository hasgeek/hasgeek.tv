<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12">
            <h1 class="mui--text-title">Remove video</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
           <div class="grid__col-xs-12">
            <p class="mui--text-title">Remove video '<b>{{video.title}}</b>' from {{playlist.title}}? This cannot be undone.</p>
            <form v-on:submit.prevent="onFormSubmit" method="POST" class="mui-form">
              <input class="mui-btn mui-btn--raised mui-btn--danger" type="submit" value="Delete"/>
              <router-link :to="{ name: 'Video', params: { video: video.url_name }}" class="mui-btn mui-btn--raised mui-btn--primary">Cancel</router-link>
              <i v-if="loading" class="material-icons mui--align-middle mui--text-display4">refresh</i>
              <div class="mui-form--error" v-html="formError"></div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import axios from 'axios';
import Utils from '../assets/js/utils';

export default {
  name: 'DeleteVideo',
  data() {
    return {
      playlist: '',
      video: '',
      path: this.$route.path,
      loading: false,
      formError: '',
      errors: [],
    };
  },
  components: {
    DisplayError: () => import('./DisplayError.vue'),
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.video = response.data.video;
      this.playlist = response.data.playlist;
    },
    onErrorJsonFetch(error) {
      this.error = error;
    },
    onFormSubmit() {
      this.loading = true;
      axios.post(this.path, {
        csrf_token: Utils.getCsrfToken(),
      })
      .then(() => {
        this.$router.push({ name: 'Playlist', params: { playlist: this.playlist.name } });
        Utils.showSuccessMessage.bind(this, 'Removed video');
      })
      .catch((e) => {
        this.loading = false;
        const errors = e.response.data.errors.error;
        Object.keys(errors).forEach((fieldName) => {
          if (Array.isArray(errors[fieldName])) {
            this.formError = `${errors[fieldName]}`;
          }
        });
      });
    },
  },
  beforeCreate() {
    this.$NProgress.configure({ showSpinner: false }).start();
    Utils.setPageTitle('Remove Video');
  },
  created() {
    Utils.fetchJson.bind(this)();
  },
};
</script>
