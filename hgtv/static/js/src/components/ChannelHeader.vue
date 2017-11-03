<template>
  <div class="content-head">
    <div class="mui-container">
      <div class="grid">
        <div class="grid__col-xs-12 grid__col-lg-6">
          <h1 id="channel-header" class="mui--text-headline">{{ channel.title }}</h1>
          <div v-html="channel.description" class="mui--text-subhead"></div>
        </div>
        <div class="grid__col-xs-12 grid__col-lg-6">
          <div class="mui--text-body2 admin-options">
            <a :href="channel.import_playlist_url" v-if="channel.import_playlist_url" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">import_export</i> Import playlist</a>
            <a :href="channel.new_playlist_url" v-if="channel.new_playlist_url" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">playlist_add</i> New playlist</a>
            <a :href="channel.edit_url" v-if="channel.edit_url" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">mode_edit</i> Edit channel</a>
            <a :href="channel.stream_add_url" v-if="channel.stream_add_url" class="admin-options__actions"><i class="material-icons mui--text-subhead mui--align-top">library_add</i> New video</a>
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
