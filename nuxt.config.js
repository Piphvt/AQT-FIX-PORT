import colors from 'vuetify/es5/util/colors'
import { th } from 'vuetify/es5/locale'; // นำเข้าภาษาไทย

export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s - AI Quant Tech Co.,Ltd',
    title: 'AQT Fix Port',
    htmlAttrs: {
      lang: 'en',
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    '@nuxtjs/vuetify', // Vuetify module
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    '@nuxtjs/axios',
    '@nuxtjs/auth-next',
  ],
  axios: {
    baseURL: 'http://localhost:3001',
    credentials: true,
  },
  auth: {
    redirect: {
      login: '/auth',
      logout: '/',
      callback: '/auth',
      home: '/app/home',
    },
    strategies: {
      local: {
        token: {
          property: 'token',
          global: true,
          required: true,
          type: 'Bearer',
        },
        endpoints: {
          login: { url: '/auth/login', method: 'post', propertyName: 'token' },
          logout: { url: '/auth/logout', method: 'delete', propertyName: 'token' },
          user: { url: '/auth/refresh', method: 'get', propertyName: 'token' },
        },
      },
    },
  },

  server: {
    port: 3000,
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ['~/assets/variables.scss'],
    theme: {
      dark: true,
      themes: {
        dark: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.darken1,
        },
      },
    },
    lang: {
      locales: { th }, // เพิ่มการตั้งค่าภาษาไทย
      current: 'th', // ตั้งค่าภาษาเป็นไทย
    },
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {},
}
