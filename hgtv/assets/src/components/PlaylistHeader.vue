<template>
  <div class="content-head">
    <div class="mui-container">
      <div class="grid grid--align-baseline">
        <div class="grid__col-xs-12 grid__col-lg-6">
          <h1 class="mui--text-title">
            <router-link :to="{ name: 'Channel', params: { channel: channel.name }}" class="mui--text-dark">{{ channel.title }}</router-link> <i class="material-icons mui--align-middle mui--text-dark mui--text-title">chevron_right</i> {{ playlist.title }}
          </h1>
          <div v-html="playlist.description"></div>
        </div>
        <div class="grid__col-xs-12 grid__col-lg-6">
          <div class="mui--text-body2 admin-options" v-if="playlist.current_action_permissions && playlist.current_action_permissions.length != 0">
            <router-link :to="{name: 'EditPlaylist', params: { channel: channel.name, playlist: playlist.name}}" v-if="playlist.current_action_permissions.includes('edit')" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">mode_edit</i> Edit playlist</router-link>
            <router-link :to="{name: 'DeletePlaylist', params: { channel: channel.name, playlist: playlist.name}}" v-if="playlist.current_action_permissions.includes('delete')" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">delete</i> Delete playlist</router-link>
            <router-link :to="{name: 'AddVideoToPlaylist', params: { channel: channel.name, playlist: playlist.name}}" v-if="playlist.current_action_permissions.includes('add-video')" class="admin-options__actions"> <i class="material-icons mui--text-subhead mui--align-top">library_add</i> Add video</router-link>
            <router-link :to="{name: 'ExtendPlaylist', params: { channel: channel.name, playlist: playlist.name}}" v-if="playlist.current_action_permissions.includes('extend')" class="extend-playlist admin-options__actions" data-method='GET'><i class="material-icons mui--text-subhead mui--align-top">playlist_add</i> Extend playlist</router-link>
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
