"""One-line descriptions for the seeded subject taxonomy (see subject_taxonomy.py).

Keyed by subject name (matches the `name` element of subject_taxonomy.SUBJECTS tuples), not by
subject_code, since the taxonomy module builds SUBJECTS from human-readable names. Used by
seed_data.py to populate Subjects.description for the initial catalog. Subjects added later
(admin-created or approved tutor proposals) get their description from the admin catalog form
instead — this module only covers what ships in the seed.
"""

SUBJECT_DESCRIPTIONS = {
    # Mathematics & Data Sciences — Core Math
    'Pre-Algebra': 'Foundational number sense, ratios, and early equation-solving before formal algebra.',
    'Algebra': 'Variables, equations, and functions — the symbolic language underlying higher math.',
    'Geometry': 'Shapes, angles, area, and proofs in two and three dimensions.',
    'Trigonometry': 'Angles and triangles, and the sine/cosine/tangent functions built from them.',
    'Pre-Calculus': 'Functions, sequences, and graphing that bridge algebra and calculus.',
    # Mathematics & Data Sciences — Advanced & Pure Math
    'Calculus': 'Limits, derivatives, and integrals for describing continuous change.',
    'Linear Algebra': 'Vectors, matrices, and linear transformations.',
    'Abstract Algebra': 'Groups, rings, and fields — the structures behind algebraic operations.',
    'Differential Equations': 'Equations relating functions to their rates of change, and how to solve them.',
    'Discrete Mathematics': 'Logic, sets, graphs, and combinatorics for reasoning about countable structures.',
    'Number Theory': 'The properties of integers — primes, divisibility, and modular arithmetic.',
    # Mathematics & Data Sciences — Applied Math & Statistics
    'Statistics': 'Collecting, summarizing, and drawing conclusions from data.',
    'Biostatistics': 'Statistical methods applied to biological and health data.',
    'Probability': 'The mathematics of uncertainty and random events.',
    'Data Analysis': 'Turning raw datasets into patterns and actionable insight.',
    'Regression Analysis': 'Modeling relationships between variables to predict outcomes.',
    'Actuarial Science': 'Applying probability and statistics to assess financial risk.',
    # Mathematics & Data Sciences — Grade Levels
    'Elementary Math': 'Arithmetic and basic problem-solving for early grade levels.',
    'High School Math': 'Algebra through pre-calculus, aligned to secondary curricula.',
    'College Mathematics': 'General-education math coursework for undergraduate programs.',
    # Natural Sciences — Physics
    'Classical Mechanics': "Newton's laws — motion, forces, and energy in everyday systems.",
    'Thermodynamics': 'Heat, work, and energy transfer between systems.',
    'Electromagnetism': 'Electric and magnetic fields, and how they interact.',
    'Quantum Mechanics': 'The physics of matter and energy at the atomic and subatomic scale.',
    'Astrophysics': 'The physics of stars, galaxies, and the universe at large.',
    'Relativity': "Einstein's theories of space, time, and gravity.",
    'Optics': 'The behavior and properties of light.',
    # Natural Sciences — Chemistry
    'General Chemistry': 'Atoms, molecules, reactions, and the periodic table.',
    'Organic Chemistry': 'The structure and reactions of carbon-based compounds.',
    'Inorganic Chemistry': 'The properties and reactions of non-carbon-based compounds.',
    'Physical Chemistry': 'How chemical systems behave at the level of energy and molecular motion.',
    'Biochemistry': 'The chemical processes underlying living organisms.',
    'Analytical Chemistry': 'Methods for identifying and measuring the composition of substances.',
    # Natural Sciences — Biology
    'Molecular Biology': 'The molecular basis of biological activity, including DNA and proteins.',
    'Genetics': 'Heredity and the variation of inherited traits.',
    'Cell Biology': 'The structure and function of cells, the basic unit of life.',
    'Human Anatomy & Physiology': 'The structure of the human body and how its systems function.',
    'Microbiology': 'Bacteria, viruses, and other microorganisms.',
    'Zoology': 'The biology, behavior, and classification of animals.',
    'Botany': 'The biology and classification of plants.',
    'Marine Biology': 'Life in oceans and other saltwater environments.',
    # Natural Sciences — Earth & Environmental Sciences
    'Ecology': 'How organisms interact with each other and their environment.',
    'Geology': "The Earth's physical structure, rocks, and processes over time.",
    'Meteorology': 'The science of weather and atmospheric conditions.',
    'Environmental Science': "Human impact on, and management of, the Earth's ecosystems.",
    'Paleontology': 'Fossils and the history of life on Earth.',
    # Technology & Computer Science — Programming Languages
    'Python': 'A general-purpose language widely used for scripting, data, and web backends.',
    'Java': 'A general-purpose, object-oriented language common in enterprise and Android apps.',
    'JavaScript': 'The scripting language that runs in browsers and powers interactive web apps.',
    'C': 'A foundational low-level language for systems and embedded programming.',
    'C++': 'An extension of C adding object-oriented features, used in performance-critical software.',
    'C#': "Microsoft's object-oriented language, common in .NET and game development (Unity).",
    'Ruby': 'A dynamic, readable language known for the Rails web framework.',
    'PHP': 'A server-side scripting language widely used for web development.',
    'SQL': 'The standard language for querying and managing relational databases.',
    'HTML & CSS': 'The markup and styling languages that structure and design web pages.',
    # Technology & Computer Science — Computer Science Theories
    'Algorithms': 'Step-by-step procedures for solving computational problems efficiently.',
    'Data Structures': 'Ways of organizing data — arrays, lists, trees — for efficient access and use.',
    'Machine Learning': 'Building systems that learn patterns from data rather than explicit rules.',
    'Artificial Intelligence': 'Building systems that perform tasks that normally require human intelligence.',
    'Cybersecurity': 'Protecting systems, networks, and data from digital threats.',
    'Database Management': 'Designing, storing, and retrieving data reliably at scale.',
    'Software Engineering': 'Principles and practices for building maintainable, reliable software.',
    'Web Development': 'Building websites and web applications, front-end and back-end.',
    # Business, Finance & Economics — Economics
    'Microeconomics': 'How individuals, households, and firms make economic decisions.',
    'Macroeconomics': 'Economy-wide phenomena — growth, inflation, and unemployment.',
    'Econometrics': 'Applying statistical methods to test economic theories against real data.',
    'Behavioral Economics': 'How psychology influences economic decision-making.',
    'International Trade': 'How and why countries exchange goods, services, and capital.',
    # Business, Finance & Economics — Accounting & Finance
    'Financial Accounting': "Recording and reporting a business's financial transactions.",
    'Managerial Accounting': 'Using financial data internally to guide business decisions.',
    'Corporate Finance': 'How companies raise capital and allocate it to maximize value.',
    'Personal Finance': 'Budgeting, saving, and managing money as an individual.',
    'Investment Banking': 'Capital raising, mergers, and advisory services for corporations.',
    'Auditing': "Independently examining an organization's financial records for accuracy.",
    # Business, Finance & Economics — Business & Management
    'Marketing': 'Promoting and selling products or services to customers.',
    'Human Resource Management': "Managing an organization's people — hiring, development, and culture.",
    'Operations Management': 'Designing and controlling the processes that produce goods and services.',
    'Entrepreneurship': 'Starting and growing new business ventures.',
    'Project Management': 'Planning and executing work to meet defined goals, scope, and timelines.',
    'Strategic Management': "Setting and executing an organization's long-term direction.",
    # Humanities & Social Sciences — History
    'World History': 'The major events and civilizations that shaped global history.',
    'European History': 'The political and cultural history of Europe.',
    'American History': 'The history of the United States, from founding to present.',
    'Ancient History': 'Early civilizations, from Mesopotamia through the classical world.',
    'Art History': 'The evolution of visual art across cultures and eras.',
    'Military History': 'Wars, warfare, and their impact on societies.',
    # Humanities & Social Sciences — Social Sciences
    'Psychology': 'The scientific study of the mind and behavior.',
    'Sociology': 'How societies, groups, and institutions function.',
    'Anthropology': 'The study of human cultures and their development.',
    'Political Science': 'Government systems, political behavior, and public policy.',
    'International Relations': 'How nations interact — diplomacy, conflict, and cooperation.',
    # Humanities & Social Sciences — Law
    'Constitutional Law': 'The interpretation and application of a constitution.',
    'Corporate Law': 'The legal rules governing businesses and corporations.',
    'International Law': 'The rules governing relations between states and international bodies.',
    'Criminal Law': 'Laws defining crimes and their punishments.',
    'Legal Writing': 'Drafting clear, persuasive legal documents and arguments.',
    # Humanities & Social Sciences — Literature & Writing
    'Literary Analysis': 'Interpreting and critiquing works of literature.',
    'Creative Writing': 'Crafting original fiction, poetry, and narrative prose.',
    'Academic Writing': 'Structuring clear, well-supported writing for academic contexts.',
    'Essay Editing': 'Refining structure, clarity, and argument in written essays.',
    'Rhetoric': 'The art of effective and persuasive communication.',
    'Journalism': 'Researching, writing, and reporting news and current events.',
    # Humanities & Social Sciences — Philosophy
    'Ethics': 'The study of right and wrong, and how we ought to act.',
    'Logic': 'The rules of valid reasoning and argument.',
    'Epistemology': 'The study of knowledge — what it is and how we acquire it.',
    'Metaphysics': 'The study of the fundamental nature of reality and existence.',
    'Political Philosophy': 'The theoretical foundations of government, justice, and rights.',
    # Hobbies & Arts — Music Theory & Instruments
    'Music Theory': 'The structure of music — scales, harmony, and notation.',
    'Solfege': 'Sight-singing and ear training using the movable-do system.',
    'Ear Training': 'Developing the ability to identify pitches, intervals, and rhythms by ear.',
    'Piano': 'Technique and repertoire for the piano.',
    'Guitar': 'Technique and repertoire for acoustic or electric guitar.',
    'Violin': 'Technique and repertoire for the violin.',
    'Drums': 'Rhythm, technique, and repertoire for the drum kit.',
    'Music Production': 'Recording, mixing, and producing music digitally.',
    # Hobbies & Arts — Visual Arts
    'Digital Art': 'Creating artwork using digital tools and software.',
    'Fine Art': 'Traditional visual art forms such as drawing and sculpture.',
    'Painting': 'Technique and composition across painting media.',
    'Graphic Design': 'Visual communication through layout, typography, and imagery.',
    'Photography': 'The art and technique of capturing images.',
}
