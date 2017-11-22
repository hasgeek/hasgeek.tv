<template>
  <div>
    <div class="content-head">
      <div class="mui-container">
        <div class="grid">
          <div class="grid__col-xs-12 grid__col-lg-6">
            <h1 class="mui--text-headline">New Playlist</h1>
          </div>
        </div>
      </div>
    </div>
    <div class="mui-container">
      <div class="page-content">
        <div class="grid">
          <div class="grid__col-xs-12 grid__col-lg-6 form-wrapper">
            <ImportForm></ImportForm>
            <div v-if="loading" class="loader-wrapper">
              <i class="material-icons loader mui--text-display3 mui--text-white">sync</i>
            </div>
            <div v-for="error in errors">
              <p class="mui-form--error mui--text-body1">{{ error[0] }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Utils from '../assets/js/utils';

let vm = {};

export default {
  name: 'ImportPlaylist',
  data() {
    return {
      path: this.$route.path,
      loading: false,
      errors: [],
    };
  },
  components: {
    ImportForm: (resolve) => {
      axios.get(vm.path)
      .then((response) => {
        resolve({
          template: Utils.getVueFormTemplate(response.data.form),
          methods: {
            onFormSubmit(event) {
              event.preventDefault();
              vm.loading = true;
              const formdata = new FormData(document.getElementById('delete'));
              axios.post(vm.path, formdata)
              .then((formResponse) => {
                vm.$router.push(formResponse.data.result.url);
              })
              .catch((e) => {
                vm.loading = false;
                vm.errors = e.response.data.errors;
              });
            },
          },
        });
      })
      .catch((e) => {
        console.log('error', e);
        vm.errors.push(e);
      });
    },
  },
  created() {
    vm = this;
  },
};
</script>

<style scoped>
</style>
