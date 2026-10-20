// Copy is exact per CLONE_SPEC.md (sections 6-10).

export const NAV = [
  { id: 'our-story', label: 'Our Story' },
  { id: 'what-we-stand-for', label: 'What we stand for' },
  { id: 'capabilities', label: 'Capabilities' },
  { id: 'our-work', label: 'Our Work' },
  { id: 'team', label: 'Team' },
]

export const MAIL = 'mailto:info@equatorcompany.com'
export const LINKEDIN = 'https://www.linkedin.com/company/the-equator-company/'

// Story blocks (section 6). Logos count as 4 "words" (positions 22-25), total 60.
export const STORY = {
  p1: 'Born from the merger of four companies with different skill sets, but the same shared values, expertise and decades of experience:',
  logos: [
    { src: '/logo_s317.png', w: 372, h: 179, alt: 'S317', href: 'https://s317consulting.com/' },
    { src: '/logo_sairdacasca.png', w: 167, h: 186, alt: 'Sair da Casca', href: 'https://www.sairdacasca.com/' },
    { src: '/logo_engidro.png', w: 356, h: 146, alt: 'Engidro', href: 'https://engidro.pt/' },
    { src: '/logo_factorsocial.png', w: 402, h: 111, alt: 'Factor Social', href: 'https://factorsocial.pt/' },
  ],
  rest: [
    { text: "What emerged isn't just bigger. It is different.", indent: false },
    { text: 'It is designed to provide a structured full-service ESG offer.', indent: true },
    { text: 'It is a unique partner for organizations seeking change.', indent: false },
    { text: 'And it is here: meet The Equator Company', indent: true, boldFrom: 5 },
  ],
  total: 60,
}

export const VALUES = [
  {
    lottie: 'sustainability',
    title: ['Sustainability,', 'made to endure'],
    cols: [
      'We embed sustainability in the foundations of economies and communities - rooted in systems, strategies, and infrastructure that endure.',
      'From energy, water and wastewater infrastructure to multiyear sustainability strategies.',
    ],
  },
  {
    lottie: 'global',
    title: ['Local legitimacy,', 'global reach'],
    cols: [
      'Born from a merger of different organizations, we combine the independence of each to create a more dynamic structure for all.',
      'Our trusted network of local partnerships across the globe aligns diverse interests, ensures delivery on the ground and delivers systemic change.',
    ],
  },
  {
    lottie: 'grounded',
    title: ['Vision grounded', 'in reality'],
    cols: [
      'Bridging ambition and execution to make transitions work, moving institutions from objectives to results. We stay close to our clients to understand their long-term vision, and deliver it:',
      'from inclusive 360º waste management blueprint to decarbonization roadmaps.',
    ],
  },
  {
    lottie: 'curiosity',
    title: ['We blend curiosity ', 'with courage'],
    cols: [
      'Engaging every challenge with curiosity and openness, bringing in fresh ideas and perspectives to discover real-world solutions.',
      'That’s how we’ve been helping turn sanitation data into better services and shaping journeys toward sustainability.',
    ],
  },
  {
    lottie: 'difference',
    title: ['Making a difference', 'and making it last'],
    cols: [
      'Our work doesn’t end at strategy handover or ribbon-cutting. We are committed to real-world impact: we design it, we implement it, and we monitor it.',
      '45+ years of experience on and off the field have shown our transformations to be not only possible but practical.',
    ],
  },
]

export const CAPABILITIES = [
  ['Sustainability Strategy', 'We design ESG strategies, implement financially sustainable action plans, ensure transparency and compliance, and mobilize stakeholders — driving sustainable growth, resilience, and measurable value for your business.'],
  ['Energy, Carbon & Biodiversity', 'We help you lead the energy transition. We design sustainable solutions, networks and hybrid systems, structure finance mechanisms, conduct environmental audits and support carbon credits certification.'],
  ['Impact & Risks', 'Integrate sustainability into your risk management and investment decisions. We assess impacts, compliance, and risk mitigation to strengthen your organizational resilience.'],
  ['Water & Sanitation', 'We promote sustainable investment in resilient infrastructure. We provide technical assistance, apply Nature-Based Solutions and ensure efficiency, safety and resilience in water and wastewater systems.'],
  ['Crisis & Communications Management', 'Prepare. Respond. Recover. We manage crises, reputation and communications to safeguard trust, continuity and institutional credibility.'],
  ['Capacity Building', 'Turn knowledge into performance: we train teams, build skills and inspire leadership for a tangible application of sustainability and the green and digital transition.'],
  ['Social & Communities', 'We create human impact. We help engage communities, promote inclusion and manage sustainable and social investments that generate lasting shared value.'],
  ['Waste & Circular Economy', 'We embed circularity into core business processes and operations. We help organisations shift from linear to circular thinking — implementing circular models, reducing waste, accelerating industrial renewal and driving long-term resilience.'],
  ['Sustainable Finance', 'Beyond buzzwords, we use the EU Taxonomy, hard-number financial modeling, blended finance and ESCO models to make your business sustainable and profitable.'],
]

const bh = (c) =>
  [
    ['0 0', c[0]], ['33% 0', c[1]], ['67% 0', c[2]], ['100% 0', c[3]],
    ['0 50%', c[4]], ['33% 50%', c[5]], ['67% 50%', c[6]], ['100% 50%', c[7]],
    ['0 100%', c[8]], ['33% 100%', c[9]], ['67% 100%', c[10]], ['100% 100%', c[11]],
  ]
    .map(([at, col]) => `radial-gradient(at ${at},${col},#00000000 50%)`)
    .join(',')

// Blurhash placeholder colours (section 9) - image data, not design tokens.
export const SLIDES = [
  {
    title: 'Forests, Carbon, and Natural Capital',
    text: 'We support governments and companies in reforestation and conservation programs, such as the 550,000-hectare project in Malawi developed with Mamaland (Mota-Engil), which generates high-quality carbon credits. We work with E-Redes on natural capital assessment and biodiversity impact optimization, transforming ecosystems into strategic assets for a regenerative economy.',
    image: '/slides/slide1',
    placeholder: bh(['#7e6d69', '#7f8381', '#866f66', '#83716c', '#807470', '#768181', '#806a65', '#7f7471', '#5d5d60', '#6c797a', '#7c706d', '#767171']),
  },
  {
    title: 'Energy and Energy Efficiency',
    text: 'We support EDP in developing and implementing renewable generation solutions including solar, wind and hydro, integrated with energy efficiency and e-mobility. Through the Effizency platform, we help utilities deliver more competitive and scalable products for both B2C and B2B markets. We also work on designing and implementing energy infrastructure for cities, industry and government, covering project management, carbon services, financing, marketing and market intelligence.',
    image: '/slides/slide2',
    placeholder: bh(['#d6dadb', '#dfdfdc', '#e3e4e0', '#e8e8e0', '#959fa3', '#9ea9b1', '#a2acb1', '#9aa6ac', '#454500', '#3d4626', '#50542e', '#636834']),
  },
  {
    title: 'Consumer Goods and Social Impact',
    text: 'We support leading retailers and consumer brands in creating social and environmental value. With SONAE MC, we developed the Missão Continente programme, which supports 900,000 people and was recognised with the 2023 European Excellence Award. We also work with major foundations and international organisations to design and implement social responsibility and circular economy policies across Europe, Asia and Africa.',
    image: '/slides/slide3',
    placeholder: bh(['#6e6f7e', '#697183', '#6a7085', '#7e7f8e', '#686c7d', '#667284', '#637087', '#787d8c', '#67707e', '#647485', '#647486', '#6a7787']),
  },
  {
    title: 'Water, Sanitation, and Resilient Cities',
    text: 'We develop climate-resilient plans and infrastructure, including the Lisbon General Drainage Plan and the Luanda Water Master Plan (2025–2045). In Portugal, we support frontier innovation in water systems. In countries such as Brazil, Angola, Mozambique, Ethiopia, Cape Verde, Malawi, Nigeria and Tanzania, we promote universal access to water and sanitation, sustainable urban drainage and integrated water resource management.',
    image: '/slides/slide4',
    placeholder: bh(['#bc6e63', '#b8193f', '#c75766', '#b74557', '#bb7148', '#b57d76', '#cc9c99', '#ae827e', '#a97346', '#ad7e79', '#c3838d', '#a87470']),
  },
  {
    title: 'Resilience and Impact',
    text: 'We assess the resilience and impact of infrastructure projects across multiple sectors, analyzing climate, economic and social risks. We develop methodologies that integrate territorial vulnerability and operational continuity, guiding investment and planning decisions. For example, we have carried out climate risk assessments for critical assets such as roads, airports and ports — including the Dallas Airport — strengthening the adaptability and safety of essential infrastructure.',
    image: '/slides/slide5',
    placeholder: bh(['#adb0a5', '#adafa1', '#a4b0a0', '#94a197', '#aba69f', '#a5a2a0', '#9ea6a7', '#7a8c93', '#aea398', '#9e938f', '#979797', '#7d808d']),
  },
]

export const MEMBER_LOGOS = [1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => `/logos/logo${n}.png`)

// role is HTML (may contain <br/>), as in the original.
export const TEAM = [
  ['Filipe de Morais Vasconcelos', 'filipe-de-morais-vasconcelos', 'Management Team', 'https://www.linkedin.com/in/filipemoraisvasconcelos/'],
  ['Miguel Feliz', 'miguel-feliz', 'Management Team', 'https://www.linkedin.com/in/miguelfeliz/'],
  ['Nathalie Ballan', 'nathalie-ballan', 'Board Member<br/>Business Development Division', 'https://www.linkedin.com/in/nathalieballan/'],
  ['Rui Marques', 'rui-marques', 'Board Member<br/>Commercial Division', 'https://www.linkedin.com/in/rui-quintas-marques-20091813/'],
  ['Ana Gonçalves', 'ana-goncalves', 'Operations Division', 'https://www.linkedin.com/in/anahgoncalves/'],
  ['Raquel Almeida', 'raquel-almeida', 'Energy, Carbon &amp; Biodiversity', 'https://www.linkedin.com/in/raquelfaalmeida/'],
  ['Cláudia Tapadas', 'claudia-tapadas', 'Sustainability Strategy', 'https://www.linkedin.com/in/claudiatapadas/'],
  ['Dalila Antunes', 'dalila-antunes', 'Impact &amp; Risks', 'https://www.linkedin.com/in/dalila-antunes-5960321/'],
  ['Marta Vian Santos', 'marta-vian-santos', 'Social &amp; Communities', 'https://www.linkedin.com/in/martaviansantos/'],
  ['Paulo Rosa', 'paulo-rosa', 'Water &amp; Sanitation', 'https://www.linkedin.com/in/paulo-rosa-9201b15/'],
  ['Rita Campos', 'rita-campos', 'Innovation', 'https://www.linkedin.com/in/rita-campos-pt/'],
  ['Teresa Cordeiro', 'teresa-cordeiro', 'Partnerships', 'https://www.linkedin.com/in/teresa-menezes-cordeiro-34a0095a/'],
  ['António Monteiro', 'antonio-monteiro', 'Industry Expert Water &amp; Sanitation', 'https://www.linkedin.com/in/ant%C3%B3nio-jorge-monteiro-78045428/'],
  ['João Guimarães', 'joao-guimaraes', 'Industry Expert Water &amp; Sanitation', 'https://www.linkedin.com/in/jo%C3%A3o-guimar%C3%A3es-60a14131/'],
  ['José Palma', 'jose-palma', 'Industry Expert Circular Economy', 'https://www.linkedin.com/in/jmpalmao/'],
].map(([name, slug, role, linkedin]) => ({ name, slug, role, linkedin }))
