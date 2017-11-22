<template>
  <div class="mui-container mui-container--no-padding-mobile">
    <div class="page-content page-content--no-padding-mobile">
      <div class="grid">
        <div :class="{ 'grid__col-xs-6': video.slides_html }" class="grid__col--no-padding-mobile grid__col-xs-12 video-box">
          <div class="video-box__video video-box__video--fixed" v-bind:class="video.video_source">
            <div v-html="video.video_iframe"></div>
          </div>
          <div class="video-box__ops video-box__details grid">
            <div class="video-box__speaker grid__col-xs-12 grid__col-lg-5">
              <p v-for="speaker in speakers" class="video-box__speaker-details">
                <a :href="speaker.playlist_for_speaking_in" class="mui--text-light mui--text-subhead"><i class="material-icons mui--text-subhead mui--align-top mui--text-light">person</i> {{ speaker.pickername }}</a>
                <a v-if="speaker.externalid" class="mui--text-light mui--text-caption">{{ speaker.externalid }}</a>
              </p>
            </div>
            <div id="video-actions" class="grid__col-xs-12 grid__col-lg-7 mui--text-right">
              <div v-if="user.logged_in">
                <span v-if="loading" class="mui--hide video-box__actions">
                  <i class="material-icons mui--align-middle mui--text-light mui--text-title">autorenew</i>
                </span>
                <button class="video-box__actions" :class="{ 'active': user.flags.starred }" title="Add to favourites" name="action" value="star"> <i class="material-icons mui--align-middle mui--text-light mui--text-title">stars</i>
                </button>
                <button class="video-box__actions" :class="{ 'active': user.flags.queued }" title="Watch this later" name="action" value="queue"> <i class="material-icons mui--align-middle mui--text-light mui--text-title">schedule</i>
                </button>
                <button class="video-box__actions" :class="{ 'active': user.flags.liked }" title="Like" name="action" value="like">
                  <i class="material-icons mui--align-middle mui--text-light mui--text-title">thumb_up</i>
                </button>
                <button class="video-box__actions" :class="{ 'active': user.flags.disliked }" title="Dislike" name="action" value="dislike">
                  <i class="material-icons mui--align-middle mui--text-light mui--text-title">thumb_down</i>
                </button>
                <div id="playlist-buttons" class="video-box__actions">
                  <a v-if="video.remove_video_url" class="video-box__actions" :href="video.remove_video_url" title="Remove from this playlist">
                    <i class="material-icons mui--align-middle mui--text-light mui--text-title">clear</i>
                  </a>
                  <div class="mui-dropdown" id="add-to-button">
                    <i class="material-icons mui--align-middle mui--text-light mui--text-title" data-mui-toggle="dropdown" title="Add to library">library_add</i>
                  </div>
                </div>
                <a class="video-box__actions" :href="video.edit_video_url" title="Edit video">
                  <i class="material-icons mui--align-middle mui--text-light mui--text-title">mode_edit</i>
                </a>
                <a class="video-box__actions" :href="video.delete_video_url" title="Delete video">
                  <i class="material-icons mui--align-middle mui--text-light mui--text-title">delete_forever</i>
                </a>
                <div class="mui-dropdown video-box__actions video-box__actions--nomargin">
                  <i class="material-icons mui--align-middle mui--text-light mui--text-title" data-mui-toggle="dropdown" title="Share">share</i>
                  <ul class="mui-dropdown__menu mui-dropdown__menu--right" id="share-buttons">
                    <li>
                      <a target="_blank" :href="shareUrl('//twitter.com/share?url=')" class="socialite twitter-share mui--text-light mui--text-title" :data-url="path" :data-text="video.title" data-via="HasGeekTV">Twitter</a>
                    </li>
                    <li>
                      <a target="_blank" :href="shareUrl('//plus.google.com/share?url')" class="socialite googleplus-share mui--text-light mui--text-title" :data-href="path" data-action="share">Google+</a>
                    </li>
                    <li>
                      <a target="_blank" :href="shareUrl('//www.facebook.com/sharer.php?u=')" class="socialite facebook-share mui--text-light mui--text-title" :data-href="path">Facebook</a>
                    </li>
                  </ul>
                </div>
              </div>
              <div v-else class="video-box__actions">
                <a class="mui-btn mui-btn--primary mui-btn--small" :href="user.login_url">Login for more options</a>
              </div>
            </div>
          </div>
        </div>
        <div v-if="video.slides_html" class="grid__col-xs-12 grid__col-lg-6">
          <div v-html="video.slides_html" class="video-box__video" v-bind:class="video.slides_source"></div>
        </div>
      </div>

      <div class="grid">
        <div class="grid__col-xs-12 mui--text-subhead video-description">
          <h3 class="mui--text-title content-head__title mui--hidden-md mui--hidden-lg mui--hidden-xl">
            <router-link :to="{ name: 'Channel', params: { channel: channel.name }}">{{ channel.title }}</router-link> <i class="material-icons mui--align-middle mui--text-hyperlink mui--text-title">chevron_right</i> <router-link :to="{ name: 'Playlist', params: { channel: channel.name, playlist: playlist.name }}">{{ playlist.title }}</router-link>
          </h3>
          <span v-if="video.not_part_playlist">Uploaded in
            <router-link :to="{ name: 'Playlist', params: { channel: channel.name, playlist: video.not_part_playlist.name}}" class="thumbnail thumbnail--video">{{ video.not_part_playlist.title }}<br /><br />
            </router-link>
          </span>
          <div v-html="video.description"></div>
        </div>
        <p v-if="relatedVideos" class="grid__col-xs-12 mui--text-title"><strong>More videos</strong></p>
        <div v-for="related_video in relatedVideos" class="grid__col-auto thumbnail-wrapper">
          <router-link :to="{ name: 'Video', params: { channel: channel.name, playlist: playlist.name, video: related_video.url }}" class="thumbnail thumbnail--video">
            <img :src="related_video.thumbnail" class="img-responsive" :alt="related_video.title"/>
          </router-link>
          <p class="mui--text-body2 video-title">{{ related_video.title }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoPlayer',
  props: ['channel', 'playlist', 'video', 'speakers', 'relatedVideos', 'user', 'path'],
  methods: {
    shareUrl(url) {
      return url + this.path;
    },
  },
};
</script>

<style scoped>
</style>
