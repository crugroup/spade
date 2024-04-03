import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Spade',
  tagline: 'Simplicity in Data Processing',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://crugroup.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/spade/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'crugroup', // Usually your GitHub org/user name.
  projectName: 'spade', // Usually your repo name.
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/crugroup/spade/tree/docs/',
        },

        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],
  plugins: [
      [
        '@docusaurus/plugin-content-docs',
        {
          id: 'extensions',
          path: 'extensions',
          routeBasePath: 'extensions',
          editUrl: 'https://github.com/crugroup/spade/tree/docs/',
        }
      ]
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Spade',
      logo: {
        alt: 'Spade',
        src: 'img/spade-logo-single.svg',
      },
      items: [
        {
          to: 'features',
          label: 'Features',
          position: 'left',
        },
        {
          type: 'docSidebar',
          sidebarId: 'spadeSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/extensions/intro',
          label: 'Extensions',
          position: 'left',
          activeBaseRegex: `/extensions/`,
        },
        {
          to: 'support',
          label: 'Support',
          position: 'right',
        },
        {
          href: 'https://github.com/crugroup/spade',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Repos',
          items: [
            {
              label: 'Spade',
              href: 'https://github.com/crugroup/spade',
            },
            {
              label: 'Spade UI',
              href: 'https://github.com/crugroup/spadeui',
            },
            {
              label: 'Spade SDK',
              href: 'https://github.com/crugroup/spadesdk',
            },
            {
              label: 'Spade Helm Chart',
              href: 'https://github.com/crugroup/spade-helm',
            },
          ],
        },
        {
          title: 'About CRU',
          items: [
            {
              label: 'CRU',
              href: 'https://crugroup.com',
            },
            {
              label: 'Careers',
              href: 'https://crugroup.com/careers/',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/crugroup',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} CRU International Ltd.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
