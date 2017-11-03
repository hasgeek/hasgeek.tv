<template>
  <div class="content-head">
    <div class="mui-container">
      <div class="grid grid--align-baseline">
        <div class="grid__col-xs-12 grid__col-lg-6">
          <h1 class="mui--text-title"><a :href="channel.url" class="mui--text-dark">{{ channel.title }}</a> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> {{ playlist.title }}</h1>
          <div v-html="playlist.description"></div>
        </div>
        <div class="grid__col-xs-12 grid__col-lg-6">
          <div class="mui--text-body2 admin-options">
            <a v-if="playlist.delete_url" :href="playlist.delete_url" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">delete</i> Delete playlist</a>
            <a v-if="playlist.add_video_url" :href="playlist.add_video_url" class="admin-options__actions"> <i class="material-icons mui--text-subhead mui--align-top">library_add</i> Add video</a>
            <a v-if="playlist.edit_url" :href="playlist.edit_url" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">mode_edit</i> Edit playlist</a>
            <a v-if="playlist.extend_url" :href="playlist.extend_url" class="extend-playlist admin-options__actions" data-method='GET'><i class="material-icons mui--text-subhead mui--align-top">playlist_add</i> Extend playlist</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'PlaylistHeader',
  props: ['channel', 'playlist'],
};
</script>

<style scoped>
</style>
