<template>
  <div class="livestream grid__col-12">
    <tabs v-if="livestreams">
      <tab v-for="(stream, index) in livestreams" :key="index" :name="'Livestream ' + getstreamIndex(index)">
        <div class="video-box">
          <div class="video-box__video">
            <iframe :id="'iframe-stream' + getstreamIndex(index)" :src="stream" frameborder="0" allowfullscreen></iframe>
          </div>
        </div>
      </tab>
    </tabs>
  </div>
</template>

<script>
export default {
  name: 'LiveStream',
  props: ['livestreams'],
  methods: {
    getstreamIndex(index) {
      return index + 1;
    },
  },
};
</script>

<style scoped>
  .video-box__video {
    padding-bottom: 56%;
    position: relative;
  }
</style>
