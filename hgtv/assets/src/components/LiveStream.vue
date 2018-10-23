<template>
  <div class="livestream grid__col-12">
    <tabs v-if="livestreams[0]">
      <tab name="Livestream 1">
        <div class="video-box">
          <div class="video-box__video">
            <iframe id="iframe-stream1" :src="livestreams[0]" frameborder="0" allowfullscreen></iframe>
          </div>
        </div>
      </tab>
      <tab name="Livestream 2" v-if="livestreams[1]">
        <div class="video-box">
          <div class="video-box__video">
            <iframe id="iframe-stream1" :src="livestreams[1]" frameborder="0" allowfullscreen></iframe>
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
};
</script>

<style scoped>
  .livestream div {
    width: 100%;
  }
  .tabs-component {
    margin: 0 0 1em;
  }
  .tabs-component-panels {
    padding: 2em 0;
  }
  .video-box__video {
    padding-bottom: 56%;
    position: relative;
  }
</style>
