<template>
  <div class="channels">
    <Event v-bind:channels="channels"></Event>
  </div>
</template>

<script>
import axios from 'axios';
import Event from '@/components/Event';

export default {
  name: 'Home',
  data() {
    return {
      channels: [],
    };
  },
  components: {
    Event,
  },
  created() {
    axios.get('/')
    .then((response) => {
      this.channels = response.data.channels;
    })
    .catch((e) => {
      this.errors.push(e);
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
