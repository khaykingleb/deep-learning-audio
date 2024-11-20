/** @type {import('semantic-release').GlobalConfig} */
export default {
  branches: ["master"],
  plugins: [
    [
      "@semantic-release/commit-analyzer",
      {
        preset: "angular",
        releaseRules: [
          {
            type: "BREAKING CHANGE",
            release: "major",
          },
          {
            type: "feat!",
            release: "major",
          },
          {
            type: "feat",
            release: "minor",
          },
          {
            message: "*",
            release: "patch",
          },
        ],
      },
    ],
    [
      "@semantic-release/release-notes-generator",
      {
        preset: "conventionalcommits",
        presetConfig: {
          header: "CHANGELOG",
          types: [
            { type: "feat", section: "Features" },
            { type: "BREAKING CHANGE", section: "Breaking Changes" },
            { type: "feat!", section: "Breaking Changes" },
            { type: "fix", section: "Bug Fixes" },
            { type: "perf", section: "Performance Improvements" },
            { type: "test", section: "Tests" },
            { type: "build", section: "Build System" },
            { type: "ci", section: "CI/CD" },
            { type: "revert", section: "Reverts" },
          ],
        },
      },
    ],
    [
      "@semantic-release/exec",
      {
        prepareCmd: "echo ${nextRelease.version} > .version",
      },
    ],
    [
      "@semantic-release/npm",
      {
        npmPublish: false,
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: ["package.json", ".version"],
        message:
          "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
    "@semantic-release/github",
  ],
};
