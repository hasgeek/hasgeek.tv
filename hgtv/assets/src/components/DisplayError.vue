<template>
  <div class="mui-container">
    <div class="page-content">
      <div class="grid">
        <div class="grid__col-xs-12">
          <p class="mui--text-subhead">{{ errorMsg }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'DisplayError',
  props: ['error'],
  data() {
    return {
      errorMsg: '',
    };
  },
  created() {
    if (this.error.response) {
      this.errorMsg = this.error.response.data;
    } else {
      this.errorMsg = 'You are offline and this page is not available on your device';
    }
  },
};
</script>

<style scoped>
</style>
