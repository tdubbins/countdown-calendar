// Vue CLI (Webpack) Environment Variable Type Definitions
// Extends NodeJS.ProcessEnv with custom environment variables

declare namespace NodeJS {
  interface ProcessEnv {
    readonly VUE_APP_API_BASE_URL?: string;
    // Add more custom env variables here as needed
  }
}
