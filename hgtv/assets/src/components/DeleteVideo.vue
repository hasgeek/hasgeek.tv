<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12">
            <h1 class="mui--text-title">Confirm delete</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
           <div class="grid__col-xs-12">
            <p class="mui--text-title">Delete video '<b>{{video.title}}</b>'? This cannot be undone.</p>
            <form v-on:submit.prevent="onFormSubmit" method="POST" class="mui-form">
              <input class="mui-btn mui-btn--raised mui-btn--danger" type="submit" value="Delete"/>
              <router-link :to="{ name: 'Video', params: { video: video.url_name }}" class="mui-btn mui-btn--raised mui-btn--primary">Cancel</router-link>
              <i v-if="loading" class="material-icons mui--align-middle mui--text-display4">refresh</i>
              <div class="mui-form__error" v-html="formError"></div>
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
      playlist: this.$route.params.playlist,
      video: '',
      loading: false,
      formError: '',
      error: '',
    };
  },
  components: {
    DisplayError: () => import('./DisplayError.vue'),
  },
  methods: {
    onSuccessJsonFetch(response) {
      this.video = response.data.video;
      this.formTemplate = Utils.getVueFormTemplate(response.data.form);
      this.formId = Utils.getElementId(this.formTemplate);
    },
    onErrorJsonFetch(error) {
      this.error = error;
    },
    onFormSubmit() {
      this.loading = true;
      axios.post(this.$route.path, {
        csrf_token: Utils.getCsrfToken(),
      })
      .then(() => {
        this.$router.push({ name: 'Playlist', params: { playlist: this.playlist } });
        Utils.showSuccessMessage.bind(this, 'Deleted video');
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
    Utils.setPageTitle('Delete Video');
  },
  created() {
    Utils.fetchJson.bind(this)();
  },
};
</script>
