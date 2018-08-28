<template>
  <div class="content-head">
    <div class="mui-container">
      <div class="grid">
        <div class="grid__col-xs-12 grid__col-lg-6">
          <h1 class="mui--text-title">
            <router-link :to="{ name: 'Home'}" class="mui--text-dark">HasGeek TV</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> {{ channel.title }}
          </h1>
          <div v-html="channel.description" class="mui--text-subhead"></div>
        </div>
        <div class="grid__col-xs-12 grid__col-lg-6">
          <div class="mui--text-body2 admin-options">
            <router-link :to="{ name: 'EditChannel', params: { channel: channel.name }}" v-if="channel.new_playlist_permission" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">mode_edit</i> Edit channel</router-link>
            <router-link :to="{ name: 'ImportPlaylist', params: { channel: channel.name }}" v-if="channel.new_playlist_permission" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">import_export</i> Import playlist</router-link>
            <router-link :to="{ name: 'AddPlaylist', params: { channel: channel.name }}" v-if="channel.new_playlist_permission" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">playlist_add</i> New playlist</router-link>
            <router-link :to="{ name: 'AddVideo', params: { channel: channel.name }}" v-if="channel.new_video_permission" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">library_add</i> New video</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChannelHeader',
  props: ['channel'],
};
</script>

<style scoped>
</style>
