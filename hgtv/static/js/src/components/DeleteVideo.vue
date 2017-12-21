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
              <router-link :to="{ name: 'Video', params: { video: video.name }}" class="mui-btn mui-btn--raised mui-btn--primary">Cancel</router-link>
              <i v-if="loading" class="material-icons mui--align-middle mui--text-display4">sync</i>
              <div class="mui-form--error" v-html="formError"></div>
            </form>
          </div>
        </div>
      </div>
    </div>
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
      path: this.$route.path,
      loading: false,
      formError: '',
      errors: [],
    };
  },
  methods: {
    onFormSubmit() {
      this.loading = true;
      axios.post(this.path, {
        csrf_token: Utils.getCsrfToken(),
      })
      .then(() => {
        this.$router.push({ name: 'Playlist', params: { playlist: this.playlist } });
      })
      .catch((e) => {
        this.loading = false;
        const errors = e.response.data.errors.error;
        Object.keys(errors).forEach((fieldName) => {
          if (Object.prototype.toString.call(errors[fieldName]) === '[object Array]') {
            this.formError = `${errors[fieldName]}`;
          }
        });
      });
    },
  },
  created() {
    axios.get(this.path)
    .then((response) => {
      this.video = response.data.video;
    })
    .catch((e) => {
      this.errors.push(e);
    });
  },
};
</script>
