<template>
  <div class="mui-container">
    <div class="page-content">
      <div class="grid">
        <div class="grid__col-xs-12">
          <p>{{ errorMsg }}</p>
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
      this.errorMsg = this.error.message;
      this.$toasted.show("You're offline", {
        theme: 'primary',
        position: 'top-right',
        icon: 'done',
        duration: 5000,
      });
    }
  },
};
</script>

<style scoped>
</style>
