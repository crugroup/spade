import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'User-friendly',
    Svg: require('@site/static/img/icon_1.svg').default,
    description: (
      <>
        Spade was designed with simplicity in mind.
      </>
    ),
  },
  {
    title: 'Efficient',
    Svg: require('@site/static/img/icon_2.svg').default,
    description: (
      <>
        Simple minimal SDK to get you started in no time.
      </>
    ),
  },
  {
    title: 'Powered by Python',
    Svg: require('@site/static/img/icon_3.svg').default,
    description: (
      <>
        Write your processes leveraging the full power of Python.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
