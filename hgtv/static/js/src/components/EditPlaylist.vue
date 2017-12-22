<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12">
            <h1 class="mui--text-title"><router-link :to="{ name: 'Playlist', params: { playlist: playlist.name }}" class="mui--text-dark">{{ playlist.title }}</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> Edit playlist</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <div class="grid__col-xs-12 form-wrapper">
            <component :is="Form"></component>
            <div v-if="loading" class="loader-wrapper">
              <i class="material-icons loader mui--text-display3 mui--text-white">sync</i>
            </div>
          </div>
        </div>
      </div>
    </div>
    <DisplayError v-if="error" :error="error"></DisplayError>
  </div>
</template>

<script>
import axios from 'axios';
import DisplayError from '@/components/DisplayError';
import Utils from '../assets/js/utils';

let vm = {};

export default {
  name: 'EditPlaylist',
  data() {
    return {
      playlist: {},
      path: this.$route.path,
      formTemplate: '',
      loading: false,
      errors: [],
    };
  },
  components: {
    DisplayError,
  },
  computed: {
    Form() {
      const template = this.formTemplate ? this.formTemplate : '<div class="mui--text-title"><i class="material-icons mui--text-title mui--align-middle">sync</i> Loading</div>';
      return {
        template,
        methods: {
          onFormSubmit() {
            vm.loading = true;
            const formdata = new FormData(document.getElementById('form'));
            axios.post(vm.path, formdata)
            .then(() => {
              vm.$router.push({ name: 'Playlist', params: { playlist: vm.playlist.name } });
            })
            .catch((e) => {
              vm.loading = false;
              Utils.showFormErrors(e.response.data.errors, vm);
            });
          },
        },
        mounted() {
          Utils.handleCancelEvent('a.mui-btn', { name: 'Playlist', params: { playlist: vm.playlist.name } }, vm);
        },
      };
    },
  },
  created() {
    vm = this;
    axios.get(this.path)
    .then((response) => {
      this.playlist = response.data.playlist;
      this.formTemplate = Utils.getVueFormTemplate(response.data.form);
    })
    .catch((error) => {
      this.error = error;
    });
  },
};
</script>

<style scoped>
</style>
