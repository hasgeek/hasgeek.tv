<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12 grid__col-lg-6">
            <h1 class="mui--text-headline">Import Playlist</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <div class="grid__col-xs-12 grid__col-lg-6">
            <form v-on:submit.prevent="importPlaylist" id="form" method="POST" data-parsley-validate accept-charset="UTF-8" class="mui-form mui-form--margins">
              <div class="mui-textfield mui-textfield--float-label">
                <input autofocus class="field-playlist_url" name="playlist_url" type="url" v-model="playlist_url">
                <label>Playlist URL</label>
              </div>
              <div class="mui-form form-actions clearfix">
                <button type="submit" class="mui-btn mui-btn--raised mui-btn--primary">Import</button>
                <a :href="back_url" class="mui-btn mui-btn--raised mui-btn--primary">Cancel</a>
                <span :class="{ 'visible': loading }" class="loader mui--align-middle"><i class="material-icons">refresh</i></span>
              </div>
              <div v-for="error in errors">
                <p class="mui-form--error">{{error[0]}}</p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ImportForm',
  data() {
    return {
      playlist_url: '',
      back_url: '',
      path: this.$route.path,
      csrf_token: '',
      loading: false,
      errors: {},
    };
  },
  created() {
    this.back_url = this.path.slice(0, this.path.indexOf('import'));
    this.csrf_token = document.head.querySelector('[name=csrf-token]').content;
  },
  methods: {
    importPlaylist(event) {
      event.preventDefault();
      this.loading = true;
      axios.post(this.path, {
        csrf_token: this.csrf_token,
        playlist_url: this.playlist_url,
      })
      .then((response) => {
        this.loading = false;
        this.$router.push(response.data.result.new_playlist_url);
      })
      .catch((e) => {
        this.loading = false;
        this.errors = e.response.data.errors;
      });
    },
  },
};
</script>

<style scoped>
</style>
