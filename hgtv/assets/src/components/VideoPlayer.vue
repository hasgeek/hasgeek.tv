<template>
  <div class="mui-container mui-container--no-padding-mobile">
    <div class="page-content page-content--no-padding-mobile">
      <div class="grid">
        <div :class="{ 'grid__col-lg-6': video.slides_html }" class="grid__col--no-padding-mobile grid__col-xs-12 video-box">
          <div class="video-box__video video-box__video--fixed" v-bind:class="video.video_source">
            <div v-html="video.video_iframe"></div>
          </div>
          <div class="video-box__ops video-box__details grid">
            <a class="grid__col-xs-12 mui--text-right mui--text-caption mui--text-light" href="https://videoken.com" target="_blank">Powered by VideoKen</a>
            <div class="video-box__speaker grid__col-xs-12 grid__col-lg-5">
              <p v-for="speaker in speakers" class="video-box__speaker-details">
                <a :href="speaker.playlist_for_speaking_in" class="mui--text-light mui--text-subhead"><i class="material-icons mui--text-subhead mui--align-top mui--text-light">person</i> {{ speaker.pickername }}</a>
                <a v-if="speaker.externalid" class="mui--text-light mui--text-caption">{{ speaker.externalid }}</a>
              </p>
            </div>
            <div id="video-actions" class="grid__col-xs-12 grid__col-lg-7 mui--text-right">
              <div>
                <div v-if="user.logged_in" class="video-box__actions video-box__actions--nomargin">
                  <button class="video-box__actions" v-on:click="submitAction('star')" title="Add to favourites" name="action" value="star" > 
                    <i class="material-icons mui--align-middle mui--text-light mui--text-title" :class="[ flags.starred ? 'mui--text-black' : 'mui--text-light' ]">stars</i>
                  </button>
                  <button class="video-box__actions" v-on:click="submitAction('queue')" title="Watch this later" name="action" value="queue"> 
                    <i class="material-icons mui--align-middle mui--text-title" :class="[ flags.queued ? 'mui--text-black' : 'mui--text-light' ]">schedule</i>
                  </button>
                  <button class="video-box__actions" v-on:click="submitAction('like')" title="Like" name="action" value="like">
                    <i class="material-icons mui--align-middle mui--text-title" :class="[ flags.liked ? 'mui--text-black' : 'mui--text-light' ]">thumb_up</i>
                  </button>
                  <button class="video-box__actions" v-on:click="submitAction('dislike')" title="Dislike" name="action" value="dislike">
                    <i class="material-icons mui--align-middle mui--text-title" :class="[ flags.disliked ? 'mui--text-black' : 'mui--text-light' ]">thumb_down</i>
                  </button>
                  <router-link :to="{name: 'RemoveVideo', params: { video: video.url_name}}" v-if="video.current_action_permissions.includes('delete')" class="video-box__actions" title="Remove from this playlist"><i class="material-icons mui--align-middle mui--text-light mui--text-title">clear</i></router-link>
                  <div id="playlist-buttons" class="video-box__actions"  v-if="video.current_action_permissions.includes('edit')">
                    <div class="mui-dropdown" v-on:click="getUserPlaylist(video.url_user_playlists)">
                      <i class="material-icons mui--align-middle mui--text-light mui--text-title" data-mui-toggle="dropdown" title="Add to library">library_add</i>
                      <PlaylistDropdown v-if="showPlaylistDropdown"></PlaylistDropdown>
                    </div>
                  </div>
                  <router-link :to="{ name: 'EditVideo', params: { channel: channel.name, playlist: playlist.name, video: video.url_name}}" v-if="video.current_action_permissions.includes('edit')" class="video-box__actions"><i class="material-icons mui--align-middle mui--text-light mui--text-title">mode_edit</i>
                  </router-link>
                  <router-link :to="{name: 'DeleteVideo', params: { video: video.url_name}}" v-if="video.current_action_permissions.includes('delete')" class="video-box__actions"><i class="material-icons mui--align-middle mui--text-light mui--text-title">delete_forever</i></router-link>
                  <span v-if="loading" class="video-box__actions">
                    <i class="material-icons mui--align-middle mui--text-light mui--text-title spin">refresh</i>
                  </span>
                </div>
                <div v-else class="video-box__actions">
                  <a class="mui-btn mui-btn--primary mui-btn--small" href="/login">Login for more options</a>
                </div>
                <div class="video-box__actions">
                  <div class="mui-dropdown video-box__actions video-box__actions--nomargin">
                    <i class="material-icons mui--align-middle mui--text-light mui--text-title" data-mui-toggle="dropdown" title="Share">share</i>
                    <ul class="mui-dropdown__menu mui-dropdown__menu--right">
                      <li>
                        <a target="_blank" :href="'//twitter.com/share?url=' + url + '&amp;via=HasGeekTV&amp;text=' + video.title" class="socialite twitter-share mui--text-light mui--text-title" :data-url="url" :data-text="video.title" data-via="HasGeekTV">Twitter</a>
                      </li>
                      <li>
                        <a target="_blank" :href="'//plus.google.com/share?url=' + url" class="socialite googleplus-share mui--text-light mui--text-title" :data-href="url" data-action="share">Google+</a>
                      </li>
                      <li>
                        <a target="_blank" :href="'//www.facebook.com/sharer.php?u=' + url + '&amp;t=' + video.title" class="socialite facebook-share mui--text-light mui--text-title" :data-href="url">Facebook</a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              <div v-for="error in errors">
                <p class="mui-form--error mui--text-body1">{{ error[0] }}</p>
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
            <router-link :to="{ name: 'Playlist', params: { channel: channel.name, playlist: video.not_part_playlist.name}}">{{ video.not_part_playlist.title }}<br /><br />
            </router-link>
          </span>
          <div v-html="video.description"></div>
        </div>
        <p v-if="relatedVideos" class="grid__col-xs-12 mui--text-subhead"><strong>More videos</strong></p>
        <div v-for="related_video in relatedVideos" class="grid__col-auto thumbnail-wrapper">
          <router-link :to="{ name: 'Video', params: { channel: channel.name, playlist: playlist.name, video: related_video.url_name }}" class="thumbnail thumbnail--video">
            <img :src="related_video.thumbnail" class="img-responsive" :alt="related_video.title"/>
          </router-link>
          <p class="mui--text-body2 video-title">{{ related_video.title }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Utils from '../assets/js/utils';

let vm = {};

export default {
  name: 'VideoPlayer',
  props: ['channel', 'playlist', 'video', 'speakers', 'relatedVideos', 'user'],
  data() {
    return {
      loading: false,
      showDropdown: false,
      showPlaylistDropdown: false,
      userPlaylist: '',
      errors: [],
    };
  },
  computed: {
    actionSubmitUrl() {
      return this.video.url_action;
    },
    flags() {
      return this.user.flags;
    },
    url() {
      return window.location.href;
    },
  },
  components: {
    PlaylistDropdown: (resolve) => {
      resolve({
        template: vm.userPlaylist,
        methods: {
          addToPlaylist(url) {
            this.loading = true;
            axios.post(url, {
              csrf_token: Utils.getCsrfToken(),
            })
            .then((response) => {
              this.loading = false;
              Utils.showSuccessMessage.bind(this, response.data.doc)();
              vm.$router.push(response.data.result.url);
            })
            .catch((e) => {
              this.loading = false;
              this.errors.push(e);
            });
          },
        },
      });
    },
  },
  methods: {
    submitAction(action) {
      this.loading = true;
      this.errors = [];
      axios.post(this.actionSubmitUrl, {
        action,
        csrf_token: Utils.getCsrfToken(),
      })
      .then((response) => {
        this.loading = false;
        this.$emit('update', response.data.result.flags);
        Utils.showSuccessMessage.bind(this, response.data.doc)();
      })
      .catch((e) => {
        this.loading = false;
        this.errors.push(e);
      });
    },
    getUserPlaylist(url) {
      if (this.userPlaylist) {
        this.showPlaylistDropdown = !this.showPlaylistDropdown;
      } else {
        this.loading = true;
        axios.get(url)
        .then((response) => {
          this.loading = false;
          this.userPlaylist = response.data;
          this.showPlaylistDropdown = true;
        })
        .catch((e) => {
          this.loading = false;
          this.errors.push(e);
        });
      }
    },
  },
  created() {
    vm = this;
  },
};
</script>

<style scoped>
</style>
