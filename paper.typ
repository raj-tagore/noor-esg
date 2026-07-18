// AI Research Paper Draft — Typst conversion
// Source: AI Research Paper Draft_ Modified on 8.1.26 (1).docx

#set document(
  title: "Leveraging Artificial Intelligence/Machine Learning (AI/ML) in Exploring the Relationship Between ESG And Corporate Financial Performance",
)
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1",
)
#set text(font: "New Computer Modern", size: 11pt, lang: "en")
#set par(justify: true, leading: 0.65em, first-line-indent: 0em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  set text(size: 14pt, weight: "bold")
  v(1.2em, weak: true)
  it
  v(0.6em, weak: true)
}
#show heading.where(level: 2): it => {
  set text(size: 12pt, weight: "bold")
  v(1em, weak: true)
  it
  v(0.4em, weak: true)
}
#show heading.where(level: 3): it => {
  set text(size: 11pt, weight: "bold")
  v(0.8em, weak: true)
  it
  v(0.3em, weak: true)
}
#show figure: set block(breakable: true)
#show figure.caption: set text(size: 9.5pt)
#set math.equation(numbering: "(1)")

#align(center)[
  #text(size: 16pt, weight: "bold")[
    Leveraging Artificial Intelligence/Machine Learning (AI/ML) in Exploring the Relationship Between ESG And Corporate Financial Performance
  ]
]

#v(1.2em)

#align(center)[
  #text(size: 11pt, weight: "bold")[Abstract]
]

#v(0.4em)
This study examines the relationship between Environmental, Social, and Governance (ESG) performance and Corporate Financial Performance (CFP) in the Banking, Financial Services, and Insurance (BFSI) sector using a firm-year panel of approximately 150 Asian BFSI firms over 2011–2025 (about 2,230 firm-year observations with non-missing profitability), combining two-way fixed-effects regression with machine-learning models (XGBoost, Random Forest, and Decision Tree). Firm-level ESG scores and Pretax Return on Assets (Pretax ROA) and Pretax Return on Equity (Pretax ROE) are obtained from the Refinitiv Eikon database. Once firm and year fixed effects are controlled and standard errors are clustered by firm, there is no statistically significant association between ESG scores and either profitability measure: the estimated ESG coefficient is small and insignificant for both Pretax ROA (β ≈ 0.001, p = 0.75; one-year lag β ≈ 0.004, p = 0.24) and Pretax ROE (β ≈ 0.001, p = 0.94; lag β ≈ 0.013, p = 0.53), with within-firm explanatory power close to zero, and firm-year correlations are negligible (r ≈ 0.01 for ROA and 0.12 for ROE). Re-estimating the same specification within country and industry groups largely reproduces this pooled null; an exploratory positive contemporaneous ESG–ROE association in China (including Hong Kong) is reported with caveats and does not overturn the overall pattern. Evaluated out-of-sample using cross-validation grouped by firm, all three machine-learning models return negative test R² values, indicating no exploitable ESG–CFP predictive signal. Descriptively, sector median ESG scores rose over the period (from about 41 to 64) while profitability remained broadly stable. An illustrative linear-trend projection to 2030 is reported for context only. Overall, once firm heterogeneity, common time shocks, and outliers are properly accounted for, ESG performance appears to be neither a robust driver nor a drag on the short-run profitability of Asian BFSI firms in this sample.

*Keywords:* Environmental Social and Governance (ESG); Banking, Financial Services, and Insurance (BFSI); Artificial Intelligence/Machine Learning (AI/ML); Corporate Financial Performance (CFP).

#pagebreak()

= Introduction

The emergence of technological innovations such as blockchain, AI, and IoT are fuelling progress towards Sustainable Development (SD) by enhancing traceability, widening financial access, and boosting transparency in corporate practices.  These technologies are shaping the way to incorporate Environmental, Social, and Governance (ESG) priorities in business operations and are becoming crucial drivers for integrating ESG principles into the strategic and operational frameworks of financial systems worldwide @laven2016. Corporates are reshaping the business strategies to align ESG with company's performance @taskin2025. The recent technological disruption in the field of as Artificial intelligence/Machine Learning (AI/ML) is also driving the ESG movement and becoming the strategic enablers for digital transformation and ESG implementation in organizations. By increasing transparency, maximising resource efficiency, and bolstering overall ESG performance, the AI/ML readiness assist organisations to achieve, and enhance sustainable outcomes @saetra2023. To supplement existing sustainability standards, legal requirements, and internal operational procedures, the AI-ESG Protocol offers a high-level, flexible agenda @wri2021. Organisations can use this protocol to find strategic opportunities, address areas for development, and openly share ESG performance with stakeholders, investors, and markets @saetra2023. Organisations are going beyond ESG impact analyses and are focusing on a comprehensive strategy that synchronises AI deployment with best practices in governance, accountability, and sustainable development @holmstrom2022.

The ESG landscape is experiencing a significant shift in recent times. The importance of ESG is being realised by non-governmental organizations, specialized consultancies, and advocacy groups focused on sustainability and social responsibility. The ESG relevance are now entering into various sectors such as lodging, transportation, resource consumption, waste management, protection of cultural heritage etc @back2024. The incorporation of ESG into investment decisions is also becoming gradually prevalent, largely driven by the growing importance of ESG ratings @clark2024. It is predicated that the global ESG assets is expected to hit \$40 trillion by 2030 @bloomberg2024. ESG now becoming a major driver in asset management: as of 2018, roughly \$17.5 trillion in assets under management representing nearly one-quarter of the \$74.3 trillion global asset management industry included ESG factors @friede2015.

Empirical studies often suggest that organizations that manage ESG risks proactively achieve stronger financial outcomes, including sturdier returns and lower portfolio volatility @friede2015. Prior work links ESG to metrics such as Pretax ROA and Pretax ROE and increasingly applies machine-learning models (decision trees, random forests, gradient boosting) to ESG–CFP questions. Results remain mixed, however, and many designs rely on aggregated or in-sample evaluation that can confuse shared time trends with firm-level association—especially when annual sector averages collapse a large firm-year panel into a handful of points. Limited evidence also exists on whether any ESG–CFP link in Asian BFSI is homogeneous across countries and business lines, or whether tree-based models retain predictive power once evaluated out of sample with firm-grouped folds. This study addresses that gap with a firm-year panel, two-way fixed-effects estimation (including country- and industry-group heterogeneity), and out-of-sample machine-learning checks, together with illustrative sector-trend projections. The research objectives are as follows.

+ *RO1.* To examine the firm-level association between ESG scores and CFP (Pretax ROA and Pretax ROE) in the Asian BFSI sector, including heterogeneity across country and industry groups.
+ *RO2.* To test whether AI/ML models can predict CFP from ESG scores under out-of-sample, firm-grouped cross-validation.
+ *RO3.* To provide policy and managerial insights, including descriptive trends and cautious forward-looking trajectories, to support informed decision-making.

The remainder of the study is organised as follows. Section 2 reviews the literature on AI/ML in the ESG context. Section 3 presents the data, exploratory diagnostics, panel fixed-effects design (including heterogeneity), and machine-learning and forecasting approach. Section 4 reports the results. Section 5 discusses the findings; Section 6 draws policy and managerial implications; and Section 7 notes limitations and directions for future research.

= Literature Review

== Artificial Intelligence/Machine Learning in the context of ESG

The Artificial Intelligence/Machine Learning (AI/ML) presents significant opportunities for exploring ESG and CFP relationship. AI enables organizations to more effectively manage and analyze ESG data, streamline compliance processes, and implement sustainable strategies with greater precision @zeng2024. AI is increasingly recognized as a critical strategic tool, providing businesses of all sizes with a competitive advantage and facilitating new avenues for growth @ferrigno2025. By leveraging AI, organizations can drive innovation, foster collaborative approaches, and enhance operational precision (xxxxxx). AI supports the development of agile capabilities, allowing firms to optimize resource utilization and improve overall efficiency (xxxxxx). In the context of ESG, AI can transforms traditional processes by automating data collection, identifying inconsistencies, and delivering real-time insights, thereby enhancing the accuracy, timeliness, and reliability of ESG disclosures (xxxx). Improved transparency in reporting strengthens stakeholder trust and contributes to enhanced organizational performance on ESG criteria (xxxx). Beyond reporting, AI is reshaping business models across the sectors, driving the next generation of economic and social value creation @francisco2023. International organizations such as United Nations, World Economic Forum, emphasize to explore AI in harnessing and advancing sustainability objectives and to promote responsible, forward-looking industry practices @francisco2023. In recent times, AI is now transitioned from a speculative concept to a core element of strategic planning, influencing operations across business, healthcare, government, and other sectors worldwide @daugherty2024. By addressing tasks that are traditionally complex, resource-intensive, or creatively demanding, AI enhances productivity, efficiency, and performance across fields such as education, marketing, finance, and manufacturing @daugherty2024. As AI-driven solutions become more prevalent, they not only transform operational and manufacturing processes but also extend into functions historically performed by humans, supporting organizations in achieving ESG objectives through responsible innovation, efficiency, and ethical decision-making @daugherty2024. The growing adoption of AI thus creates substantial opportunities for advancing in ESG, improving the quality and effectiveness of decision-making for all stakeholders @teichmann2024. By establishing robust AI-driven channels for engaging external stakeholders, organizations can enhance their appeal to ESG-focused investors and potentially realize improved financial returns @shahzad2020.

In recent years, there has been growing interest in the intersection of ML and ESG within finance and accounting research @li2025. The abundant availability of financial and accounting data, combined with the complex and often subtle interrelationships among key variables, makes these fields particularly well-suited for the application of ML @kelly2023. The ML techniques in finance and accounting studies have expanded rapidly, with an annual average of over 300 such papers published between 2020 and 2024 @li2025. The versality of ML enables researchers to analyze extensive and unconventional datasets, ranging from job advertisements, earnings call transcripts, media reports with a level of depth and granularity not achievable through traditional approaches @li2025. By contrast, conventional asset pricing frameworks, such as the Capital Asset Pricing Model (CAPM) and the Fama–French three-factor model, rely on linear relationships between a limited set of risk factors and expected returns (xxxx). These models assume that market dynamics are relatively stable and that factor-return relationships remain straightforward over time @ferrara2024. In practice, financial markets are far more complex, characterized by non-linear interactions, evolving relationships, and massive volumes of data, creating conditions in which ML offer significant advantages @khandani2010. Table 1 provides a summary of earlier studies exploring the ESG and AI/ML research.

#set text(size: 7.5pt)
#figure(
  table(
    columns: (0.9fr, 0.55fr, 1.1fr, 1.0fr, 1.1fr, 1.1fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header(
      [*Author & year*],
      [*Region*],
      [*Research Focus*],
      [*Methodology*],
      [*Findings*],
      [*Limitations*],
    ),
      [Liu and Shen., (2025)],
      [China],
      [To explore the AI development, operationalizing it the introduction of AI Pilot Zones and its effects on corporate ESG performance.],
      [CSMAR, Difference-in-Differences (DID) approach.],
      [AI policy significantly improves ESG performance.],
      [Sample restricted to a share listed company, however, the understanding of AI in business practices remains limited. Granular evidence presented for environmental and social practices,],
      [Du and Chen., (2025)],
      [China],
      [To analyse how AI technologies can be applied to advance sustainable project management practices.],
      [Wind AI Concept Index and ESG300 Index, Vector Autoregression (VAR) Granger causality.],
      [The rapid tech growth, policy shifts and ESG investments promote sustainable and responsible AI.],
      [The empirical analysis is limited to China, making direct generalization to other geographical contexts remains uncertain. Further studies exploring emerging Asian economies becomes paramount.],
      [Yu et al., (2025)],
      [China],
      [To analyse AI and ESG relationship],
      [Cloud services, AI data mapping.],
      [Double materiality covering outbound sustainability impacts & inbound financial risks is recommended for a holistic assessment.],
      [Flexibility may reduce the protocol’s utility for entities seeking directly comparable, strictly quantitative data between companies.],
      [Liu et al., (2025)],
      [China],
      [To study the ESG benefits of adopting AI],
      [DOI, TOE models, Sustainanalytics, MSCI, S&P Global.],
      [Leading ESG firms are actively adopting AI, particularly in natural language processing (NLP).],
      [The study relies on publicly available data which may not capture full internal practices or strategy.],
      [Deberdt et al., (2025)],
      [USA, Canada],
      [To investigate the role of AI in enhancing ESG practices within supply chain management (SCM).],
      [Critical review, cross sector analysis.],
      [Direct benefits across all sectors of ESG, helps with IUU fishing detection and stock management but may deepen overfishing risks and access inequalities.],
      [AI models need extensive, high-quality data, which is often lacking, especially in remote or less-regulated sectors.],
      [Aljohani., (2025)],
      [Saudi Arabia],
      [Examine the environmental challenges and opportunities of generative AI (GenAI) in the context of sustainability.],
      [Fuzzy TOPSIS, MCDM.],
      [Renewable energy integration, AI-powered predictive analytics, sustainable supply chain optimization.],
      [Expert input bias, current implementation is tailored to the manufacturing sector only.],
      [Li., (2025)],
      [Canada],
      [To explore big data and diverse Machine Learning techniques are applied in ESG research in finance and accounting.],
      [Bag of Words, LDA, HDP, ClimateBERT, XGBoost.],
      [Rapid growth in ESG + ML research since 2018, especially in climate risk analysis and textual ESG measures.],
      [No contextual understanding; risk of false positives from ambiguous keywords, need for theory-driven ML applications.],
      [Işık et al., (2025)],
      [Turkey],
      [The study investigates the interplay between AI, ESG principles and sustainable tourism, examining how AI-driven practices can foster economic growth.],
      [Applied advanced statistical models, including regression-based approaches.],
      [The combined use of AI and ESG strategies can help the tourism industry meet sustainability targets while maintaining financial growth.],
      [The study focuses on economic and operational dimensions, with less emphasis on social or cultural impacts beyond ESG metrics.],
      [Heever et al., (2025)],
      [Singapore],
      [The study examines how neurosymbolic AI combined with structured reasoning of symbolic AI can be applied to analyze key ESG aspects in the context of socially responsible investing.],
      [Harvested 300,000 ESG-related tweets using X (formerly Twitter).],
      [Environment, social impact, governance quality, sustainability, ethics, diversity, and compliance emerged as the most influential factors shaping investor perception.],
      [captures correlations in sentiment and topics but cannot definitively establish causal links between public discourse and investment performance.],
      [Mustafa et al., (2025)],
      [UK],
      [To critically examines how AI can be harnessed to improve sustainability reporting, especially with regard to ESG disclosures.],
      [PRISMA and SPAR-4-SLR, Scopus and Web of Science, ABS 3, 4, 4\* or SJR Q1 journals.],
      [Research in AI and sustainability reporting has increased notably since 2015, correlating with global policy shifts (e.g., Paris Agreement).],
      [Limited to peer-reviewed journal articles from select databases, missing significant contributions in industries, conference literature, and non-English sources.],
      [Tian et al., (2025)],
      [China],
      [To study the integration of AI technologies by companies influences their ESG performance.],
      [Shanghai & Shenzhen stock exchanges, CSMAR database, Propensity Score Matching (PSM).],
      [Higher AI adoption is strongly associated with improved ESG scores.],
      [Text-based AI indicators, while innovative, may misclassify AI mentions that are strategic rather than operational.],
      [Weng., (2025)],
      [China],
      [To study the integration of AI technologies within China’s manufacturing sector impacts corporate ESG performance.],
      [CSI ESG Ratings, CSMAR & WIND databases, MD&A.],
      [ESG impact of AI adoption is partially transmitted via these innovation improvements, confirming green innovation’s intermediary role.],
      [Focus limited to Chinese A-share listed manufacturing firms; results may not generalize to SMEs, other industries, or international contexts.],
      [Taskin et al., (2025)],
      [Turkey],
      [To determine if historical ESG scores or grades alone are sufficient predictors of future ESG performance],
      [Time Series Data, Input and Target Variables, Decision Tree (DT), Random Forest (RF), K-Nearest Neighbor (KNN), Logistic Regression (LR), Root Mean Square Error (RMSE)],
      [All four algorithms (especially KNN and RF) predict future ESG scores with 89–92% accuracy (MAPE 8–10%) using only the past three years' scores, even on an external test set.],
      [The sample only covers Turkish companies (BIST Sustainability Index), so the generalizability to developed markets is uncertain.],
      [Giri and Chaparro., (2024)],
      [Spain],
      [To understand the specific features of AI adoption by major ESG rating agencies, including the types of AI technologies used, their functional applications, the level of innovation, and adoption intensity.],
      [Content analysis, Diffusion of Innovation (DOI), Technology -Organization-Environment models.],
      [Machine Language innovations for sustainability assessments, realized effects of AI integration.],
      [Prior literature failed to explore how and to what extent AI is used by ESG raters.],
      [Lim., 2024],
      [Singapore],
      [AI in Finance; examines applications of XAI across various domains such as healthcare, finance, and autonomous systems.],
      [PRISMA protocol, LDA, pyLDAvis, Louvain algorithm.],
      [8 major research archetypes with Trading & Investment as the most crowded, research output, interest surged post-2018, suggesting a rapidly maturing field.],
      [Heavy reliance on Google Scholar, some AI domains are underrepresented due to recency and rapid field evolution.],
      [Leuthe et al., 2024],
      [Germany],
      [What design patterns can ML development stakeholders incorporate to increase the sustainability of the ML development process?],
      [Design Science Research (DSR), SML-DPM.],
      [Bigger is better" (e.g., huge ML models, large datasets) does not always hold for sustainability; smart choices often bring better balance across ESG.],
      [Patterns are intentionally abstract ,not instantly ready-to-use engineering recipes; further work is needed to operationalize them for specific industry contexts.],
      [Ferrara and Ciano., 2024],
      [Italy],
      [examines the ways in which artificial intelligence can be leveraged to advance the United Nations Sustainable Development Goals.],
      [SGD, Conceptual mapping.],
      [AI holds considerable promise for accelerating progress toward multiple SDGs by enhancing efficiency.],
      [The research is largely theoretical and relies on secondary sources, with no primary empirical testing or quantitative measurement.],
      [Chen et al., 2024],
      [Japan],
      [The study analyzes whether and how Environmental, Social, and Governance (ESG) activities impact the market value of publicly traded companies in Japan.],
      [Natural Language Processing (NLP) techniques, Difference-in-Differences (DID) approach.],
      [Companies registering higher AI-derived ESG scores consistently show higher Tobin’s Q values, meaning ESG initiatives generally increase firm value in the Japanese context.],
      [AI-based ESG measure is a “disclosure score” derived from self-reported text, and does not distinguish between positive and negative contextual use of ESG terms, which may introduce bias in the score.],
      [Chen et al., 2024],
      [China],
      [This study scrutinizes whether and how artificial intelligence (AI) adoption sways the ESG performance of publicly traded companies in China.],
      [panel data from Chinese A-share listed firms from 2007 to 2022, Tobin’s Q, Bloomberg scores.],
      [Businesses that incorporate AI technologies tend to achieve higher ESG ratings. For every 1% increase in measured AI activity, corporate ESG scores increase by 0.018%.],
      [relies on keyword frequency in annual reports, may not perfectly capture the depth or quality of AI deployment, and could be influenced by superficial mentions.],
      [Avramov et al., 2024],
      [Israel],
      [how dynamic ESG demand and supply influence risk premia, convenience yields, and realized return spreads between green and brown portfolios.],
      [Epstein-Zin utility framework, MSCI, Kalman filter, Structural Vector Autoregression (SVAR).],
      [Green assets earn positive risk premia for exposure to ESG demand shocks, offset by negative premia (convenience yield) because investors derive utility simply from holding them. Brown assets have the opposite profile.],
      [The empirical analysis is restricted to US equities with available MSCI ESG scores, which may not generalize internationally or to other asset classes.],
      [Li et al., 2024],
      [Japan],
      [The goal is to quantitatively analyze the relatedness and sentiment of over 2 million news reports to track public attitude shifts towards ESG issues, offering insights for policymakers, businesses, and academia.],
      [NLP techniques, Text Match Pre Trained Performer TMTP, (distilroberta-finetuned-financial-news-sentiment-analysis, DFFNSA, from HuggingFace)],
      [Over the two-year window, US media increased focus on social issues (such as labor rights, unemployment, poverty, and inequality), while coverage of environmental topics (notably air pollution and greenhouse gas) declined.],
      [The pre-trained sentiment model was not further fine-tuned for ESG content; its financial news training corpus and max input size (512 tokens) may not optimally capture nuances in ESG-related articles.],
      [Burnaev et al., 2023],
      [Russia],
      [ESG Challenges.],
      [PRISMA review method, scientific papers, Scopus.],
      [Most practical results are found where abundant data is available e.g, satellite imagery in ecology, digital records in governance.],
      [Does not assess AI tool prevalence or statistical trends across ESG topics, focusing on representative, detailed case studies.],
      [Chung et al., 2023],
      [Vietnam],
      [investigates the relationship between ESG performance and risk management in the hospitality sector.],
      [Panel data from publicly listed hotel firms in the U.S.],
      [Hotels with stronger ESG performance demonstrated higher operational efficiency, suggesting that ESG investments contribute to cost reduction and productivity improvements.],
      [While correlations are established, definitive causal relationships between ESG investments and operational efficiency remain unproven.],
      [Vitto et al., 2023],
      [Italy],
      [aims to address the lack of transparency in how ESG scores are calculated by rating agencies, focusing on Refinitiv’s proprietary scoring framework.],
      [Refinitiv’s Eikon platform aka Asset4, Linear Regression, Lasso, Ridge, RMSE, MAE.],
      [ESG scores can be closely approximated through relatively simple regression models with similar performance to complex ANNs.],
      [complex ML models could not eliminate unexplained variance, suggesting randomness or undisclosed adjustments within Refinitiv’s system.],
      [Lo et al., 2023],
      [USA],
      [How does impact investing affect investment performance compared to traditional portfolios?],
      [linear multifactor asset pricing model, induced order statistics, Treynor–Black portfolio construction, empirical calibrations and case studies],
      [The framework clarifies why empirical results for impact and ESG investing are often inconsistent, pointing to heterogeneous definitions, models, asset types, market regimes, and the critical role of measurement error.],
      [The results are always relative to a chosen benchmark model; different choices (e.g., number of factors) can yield fundamentally different conclusions about the value of impact investing],
      [Moss et al., 2023],
      [USA],
      [to empirically test if firm-initiated ESG press releases drive observable portfolio adjustments among retail investors in actual market settings, contrasting previous literature mainly based on mutual fund flows or experimental surveys.],
      [Robinhood (via Robintrack), CSRWire and RavenPack, Subsample analyses, TVL Pulse Score data],
      [Across all measures, retail investors did not materially adjust positions in response to ESG press releases, with coefficients indistinguishable from routine nonevent-day activity. By contrast, non-ESG press releases and especially earnings announcements led to significant changes in portfolio holdings among retail investors.],
      [Robinhood users may not be fully representative of all retail investors, though additional tests using alternate methods support findings. Analysis is short-term around press release dates and does not address longer-term portfolio rebalancing or the use of ESG information in periodic decision processes.],
      [Saetra., 2022],
      [Norway],
      [aims to fill a gap in current ESG and sustainability reporting frameworks, which often do not specifically address the unique impacts and risks associated with AI and data-intensive operations.],
      [Mixed methods approach, Greenhouse Gas protocols scope, GRI, EU Taxonomy.],
      [The current ESG reporting and ratings landscape is fragmented and lacks comparability, especially for technology-driven impacts.],
      [The protocol is a high-level tool and does not offer sector-specific or fully quantitative metrics.],
      [Minkkinen et al., 2022],
      [Finland],
      [to critically examine the implications of artificial intelligence (AI) for education through the lens of ethics and societal impact.],
      [Five senior-level Finnish experts in ESG investing, responsible AI, semi-structured interviews.],
      [Low investor awareness, critical lack of standardized metrics for assessing responsible AI at an organizational level.],
      [Small, localized sample, No statistical or prevalence data, findings are interpretive and exploratory.],
      [Khoruzhy et al., 2022],
      [Russia],
      [analyze AI-driven digital technologies on ESG investment practices, and to propose tailored recommendations for each country group to maximize the effectiveness of sustainable investment.],
      [ICT infrastructure, Morningstar and UNCTAD, 2021, SWOT.],
      [In developed countries, ICT and R&D institutions play a major role in supporting ESG investment. However, skills, industry, and finance have a relatively small impact despite moderate development.],
      [The analysis generalizes "developed" and "developing" countries as broad categories, overlooking unique national conditions and the specifics of ESG investment within each nation.],
      [Raza et al., 2022],
      [Pakistan],
      [The article centers on utilizing AI ML models, to predict ESG pillar scores for non-financial companies in the USA, UK, and Germany.],
      [New York , London and Frankfurt Stock Exchange, ROA, ROE, EPS, EBIT, K-Nearest Neighbor(KNN), Polynomial Regression (up to degree 5).],
      [Among all ML methods, artificial neural networks (ANN), especially those with multiple hidden layers and optimal neuron counts, produce the lowest RMSE and MAE values, demonstrating the highest accuracy in ESG score prediction.],
      [Due to data constraints, the research period was restricted to 2008–2020; future studies could extend the analysis to more recent data.],
      [Dai and Tang., 2021],
      [USA],
      [The paper investigates the critical intersection between Environmental, Social, and Governance (ESG) measures and end-to-end supply chain management, especially in the wake of the COVID-19 pandemic.],
      [MSCI, In-depth case studies],
      [Supply chain opacity and lack of transparency. Ambiguous relationship between ESG supply chain measures and firm performance. Complexity and overload of potential ESG supply chain metrics. Inconsistent and uneven legal/regulatory enforcement across countries and industries.],
      [The paper points out that current ESG and supply chain data availability is limited, and different methodologies or definitions between rating agencies can create confusion until harmonized standards emerge.],
      [Kim and Yoon., 2020],
      [South Korea],
      [The research investigates the actual ESG follow-through of active U.S. mutual fund managers after they sign the United Nations Principles for Responsible Investment (UN PRI), which is the world’s largest ESG initiative in the asset-management industry.],
      [longitudinal event study and difference-in-differences design, MSCI, Sustainalytics, TruValue Labs, CAPM Alpha],
      [Fund inflow increases significantly after funds sign the PRI (average 4.9% per quarter for six quarters post-signing), suggesting PRI affiliation is a strong signal for attracting capital. There is no meaningful improvement in fund-level ESG scores or returns following PRI signing.],
      [The research can only assess outcome-based measures, such as portfolio-level ESG scores and fund flows; it cannot directly observe managers’ intentions, internal processes, or private engagements. Proprietary ESG scoring systems developed by some asset managers are not captured due to lack of disclosure.],
  ),  caption: [The ESG and AI/ML research landscape],
) <tab:esg-aiml-landscape>

#set text(size: 11pt)

#set text(size: 8.5pt)
#figure(
  table(
    columns: (1.1fr, 1.4fr, 1.2fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header(
      [*Models*],
      [*ESG-Finance Analysis*],
      [*References*],
    ),
      [Gradient Boosting (XGBoost), Random Forest (RF), Decision Trees and Linear Regression, LightGBM, Multichannel CNN, Bidirectional Gated Recurrent Units (BiGRU), K-Nearest Neighbor (KNN)],
      [Gradient Boosting (XGBoost) → Predict ESG scores, stock returns, credit risk, firm valuation.],
      [(Chen et al., 2024), (Kai Li et al., 2025), (Ferrera, 2024), @taskin2025],
      [],
      [Random Forest (RF), Decision Trees, Linear Regression → Robust ESG rating prediction; handles non-linear ESG–financial data, ESG score prediction/financial performances, supports investment decisions.],
      [(Chen et al., 2024), (Kai Li et al., 2025), (Ferrera, 2024), @taskin2025, (Vitto et al., 2023), @raza2022,],
      [],
      [LightGBM → High-speed ESG risk modeling on large datasets.],
      [(Chen et al., 2024), (Kai Li et al., 2025)],
      [],
      [K-Nearest Neighbor (KNN) → ESG firm classification, peer benchmarking, sector clustering.],
      [(Li et al., 2025), @raza2022, @taskin2025],
      [],
      [Deep Neural Networks (DNNs) → modeling complex nonlinear relationships in ESG and financial data.],
      [(Burnaev et al., 2023), (Kai Li et al., 2025), (Chen et al., 2024)],
      [],
      [Multichannel CNN (Convolutional Neural Networks) → extracting spatial and temporal features from structured and unstructured ESG data.],
      [(Burnaev et al., 2023), (Heever et al., 2025)],
      [],
      [Bidirectional Gated Recurrent Units (BiGRU) → model sequential and time-series ESG-finance data for tasks like sentiment analysis.],
      [(Heever et al., 2025), (Kai Li et al., 2025)],
      [Neural ODEs, Gaussian Processes (time dynamics) \[PatchGAN, Wasserstein GANs (WGAN), Informed Neural Networks (PINNs)\], Neural Point-Based Graphics (NPBG++)],
      [Neural ODEs → Continuous-time ESG dynamic modeling.],
      [(Kai Li et al., 2025), (Burnaev et al., 2022)],
      [],
      [Gaussian Processes → ESG uncertainty quantification in time-series forecasts.],
      [(Kai Li et al., 2025), (Burnaev et al., 2022)],
      [Propensity Score Matching (PSM)],
      [Propensity Score Matching (PSM) → Compare ESG-adopting vs. non-adopting firms.],
      [(Liu et al., 2025), @tian2025],
      [BERT / ClimateBERT, LDA (Latent Dirichlet Allocation), Hierarchical Dirichlet Process (HDP), Correlated Topic Models (CTM), SenticNet],
      [BERT / ClimateBERT  ESG text classification, greenwashing detection, predict earnings calls.],
      [(Liu et al., 2025), (Burnaev et al., 2023), (Kai Li et al., 2025), (Ferrera, 2024), (Heever et al., 2025)],
      [],
      [Natural Language Processing (NLP) → ESG disclosure parsing, sentiment analysis.],
      [(Giri et al., 2024), (Liu et al., 2025), (Aljohani et al., 2025), (Li et al., 2025), (Heever et al., 2025), (Chao Li et al., 2024)],
      [],
      [LDA, HDP, CTM (Topic Models) → Identify ESG themes in reports & media.],
      [(Lim et al., 2024), (Kai Li et al., 2025), (Vitto et al., 2023)],
      [],
      [SenticNet → Emotion-driven ESG sentiment detection.],
      [(Heever et al., 2025), (Vitto et al., 2023)],
      [LDA, HDP, CTM (also clustering topic models), K-Means, DBSCAN (implied under ESG research clustering)],
      [LDA, HDP, CTM (as clustering) → ESG topic grouping.],
      [(Kai Li et al., 2025), (Vitto et al., 2023)],
      [],
      [K-Means, DBSCAN → Identify ESG company archetypes, peer groups.],
      [(Kai Li et al., 2025), (Vitto et al., 2023)],
  ),  caption: [The forecasting models used by earlier researchers.],
) <tab:forecasting-models>

#set text(size: 11pt)

= Research Methodology

== Data

Firm-level ESG scores and financial performance data for the Banking, Financial Services, and Insurance (BFSI) sector were obtained from the Refinitiv Eikon database for 2011–2025. The sample comprises approximately 150 BFSI firms headquartered across Asian markets (including Japan, China, Hong Kong, Turkey, Saudi Arabia, India, and Malaysia) that consistently disclosed ESG information for at least five years. Because each firm is observed over up to 15 fiscal years, the working dataset is a firm-year panel of 2,250 firm-years (2,230 with non-missing ROA; 2,225 with non-missing ROE), not a set of annual sector averages.

Three variables are used:

- *ESG Score* — a composite Refinitiv metric combining environmental, social, and governance performance on a 0–100 scale.
- *Pretax Return on Assets (ROA)* — pretax income divided by total assets (%).
- *Pretax Return on Equity (ROE)* — pretax income divided by shareholders' equity (%).

ROA and ROE are ratios whose denominators (assets, equity) can collapse toward zero for a distressed firm, producing economically meaningless extremes. For example, one firm posted a 2020 ROE of roughly −4,162% after its equity was almost entirely eroded, even though its ROA that year was only modestly negative. A single such value can dominate a sector mean and distort regression estimates. To prevent this, ROA and ROE are winsorized at the 1st and 99th percentiles (pooled across all firm-years); raw values are retained for transparency.

Annual sector means and medians are computed purely to describe broad trends. They are *not* used for correlation, regression, or model training, because averaging roughly 150 firms into a single number per year discards the cross-firm variation needed to identify any ESG–performance relationship and reduces the data to just 15 points, which produces spurious, trend-driven associations.

#figure(
  table(
    columns: (2fr, 1fr, 1fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header([*Institution Type*], [*Count*], [*Percentage*]),
    [Commercial Banks], [97], [64.7%],
    [Life and Health Insurance], [16], [10.7%],
    [Investment Banking & Brokerage], [12], [8.0%],
    [Consumer Lending], [9], [6.0%],
    [Other Financial Services], [16], [10.6%],
    [Total], [150], [100%],
  ),
  caption: [Dataset composition by institution type],
) <tab:dataset-composition>

=== Exploratory sample diagnostics

Before inference, a descriptive atlas of the firm-year panel is produced (figures under `outputs/explore/`). Single-dimension composition charts show raw headquarters country (`country_hq`) and TRBC industry labels. Multi-series and faceted figures use the *same* geography- and industry-based analysis groups as the heterogeneity regressions (Japan; China incl. Hong Kong; Korea; Taiwan; India; ASEAN; West Asia / Middle East; and Banks / Insurance / Other financials). Exact uncollapsed counts are retained in the composition summary and in the single-dimension bar charts.

In this sample the panel has 150 firms and 2,250 firm-years (2011–2025). Headquarters coverage is led by Japan (37), China (17), South Korea (16), India (13), and Taiwan (13). By industry, Banks predominate (97), followed by Life & Health Insurance (16) and Investment Banking & Brokerage Services (12). ESG is non-missing in all firm-years; pretax ROA and ROE are available for 99.1% and 98.9% of firm-years respectively.

The figures below are for sample understanding only. Median trajectories and faceted ESG–ROA scatters are *not* used for correlation, regression, or causal claims; those rest on the panel fixed-effects results in Section 4.

#figure(
  image("outputs/explore/01_composition_country.png", width: 90%),
  caption: [Distinct firms by headquarters country],
) <fig:explore-country>

#figure(
  image("outputs/explore/02_composition_industry_heatmap.png", width: 95%),
  caption: [Industry composition and country-group × industry-group firm-count heatmap],
) <fig:explore-industry>

#figure(
  image("outputs/explore/03_coverage_over_time.png", width: 90%),
  caption: [Non-null ESG / ROA / ROE firm-year counts by calendar year],
) <fig:explore-coverage-time>

#figure(
  image("outputs/explore/04_coverage_by_country.png", width: 90%),
  caption: [ESG coverage rate and median years of ESG history per firm, by country group],
) <fig:explore-coverage-country>

#figure(
  image("outputs/explore/05_univariate_distributions.png", width: 95%),
  caption: [Firm-year distributions of ESG, pretax ROA, and pretax ROE (ROA/ROE winsorized)],
) <fig:explore-univ>

#figure(
  image("outputs/explore/06_distributions_by_group.png", width: 95%),
  caption: [Box plots of ESG and ROA by industry and by country group],
) <fig:explore-box>

#figure(
  image("outputs/explore/07_median_trajectories_by_group.png", width: 95%),
  caption: [Median ESG over time by country group and by industry (descriptive only)],
) <fig:explore-traj>

#figure(
  image("outputs/explore/08a_esg_vs_roa_by_industry.png", width: 95%),
  caption: [Firm-year ESG versus pretax ROA, faceted by industry group (Banks / Insurance / Other financials)],
) <fig:explore-scatter-ind>

#figure(
  image("outputs/explore/08b_esg_vs_roa_by_country.png", width: 95%),
  caption: [Firm-year ESG versus pretax ROA, faceted by analysis country group (same groups as FE heterogeneity)],
) <fig:explore-scatter-cty>

== Primary model: panel fixed-effects regression

The core inferential model is a two-way (firm and year) fixed-effects panel regression, estimated on the full firm-year panel. For firm $i$ in year $t$:

$ Y_(i t) = alpha_i + gamma_t + beta · "ESG"_(i t) + epsilon_(i t) $<eq:panel-fe>

where $Y_(i t)$ is Pretax ROA or Pretax ROE; $alpha_i$ is a firm fixed effect absorbing time-invariant firm characteristics; $gamma_t$ is a year fixed effect absorbing macro-financial shocks common to all firms in a given year; $beta$ is the coefficient of interest, capturing the within-firm association between ESG and performance; and $epsilon_(i t)$ is the idiosyncratic error.

Standard errors are clustered by firm to account for within-firm serial correlation. The model is estimated in both a contemporaneous form ($"ESG"_(i t)$) and a one-year-lagged form ($"ESG"_(i,t-1)$), the latter allowing current profitability to respond to prior ESG effort. Because the firm and year fixed effects remove the shared time trends that drive spurious correlations in aggregated data, $beta$ identifies whether changes in a firm's own ESG score are associated with changes in its own profitability.

For descriptive comparison, Pearson correlations between ESG and each financial metric are also reported at the firm-year level (across all observations, not on yearly averages).

=== Heterogeneity by country group and industry

To check whether the pooled null result masks differences across markets or business lines, the same two-way FE estimator is re-estimated on geography- and industry-based subsamples. Group membership is defined by region / market identity first; firm counts only determine whether a country is estimated alone or remains inside its regional pool. There is no catch-all "Other" of unrelated small markets.

#figure(
  table(
    columns: (1.2fr, 2fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header([*Group*], [*Members*]),
    [Japan], [Japan],
    [China (incl. Hong Kong)], [China, Hong Kong],
    [Korea], [Korea; Republic (S. Korea)],
    [Taiwan], [Taiwan],
    [India], [India],
    [ASEAN], [Malaysia, Indonesia, Thailand, Singapore, Philippines],
    [West Asia / Middle East], [Turkey, Israel, Kuwait, Jordan, Oman, Qatar, Saudi Arabia],
  ),
  caption: [Country groups used in heterogeneity analysis (`country_hq`)],
) <tab:country-groups>

Industry groups (TRBC) are Banks; Insurance (Life & Health + Property & Casualty); and Other financials (remaining industries). A subsample is estimated only if it has at least 10 firms and 100 firm-years with usable ESG and outcome data. Contemporaneous and one-year-lagged ESG specifications are reported. The exploratory plots above are not substitutes for these regressions.

== Machine-learning models and out-of-sample validation

Three tree-based models—XGBoost, Random Forest, and Decision Tree—are used to test whether ESG has any (possibly non-linear) predictive value for financial performance. Performance is measured out-of-sample only, using $k$-fold cross-validation with folds grouped by firm (`GroupKFold`), so that all observations of a given firm fall entirely within either the training or the test partition. Both training and test scores are reported; a large gap between them reveals overfitting. Evaluating a model on the same rows used to fit it yields near-perfect $R^2$ by memorization and is not evidence of predictive power.

== Forecasting

Tree-based models cannot extrapolate beyond the range of their training data, so they are not used for projection. Instead, an illustrative linear-trend (ordinary least squares) forecast is fitted to the annual median series, with 95% prediction intervals. Given only 15 annual observations, these projections are explicitly illustrative and carry wide uncertainty.

== Evaluation metrics

Model fit is quantified with the coefficient of determination ($R^2$, reported out-of-sample), root mean squared error (RMSE), and mean absolute error (MAE). Statistical significance of regression coefficients is assessed with firm-clustered $t$-statistics and associated $p$-values, using a 5% threshold.

= Results and Key Findings

== Descriptive statistics and historical trends

Over 2011–2025, sector ESG scores rose markedly while profitability was broadly stable. @tab:desc-stats reports the pooled firm-year distribution; @tab:annual-medians shows the annual median trajectory.

#figure(
  table(
    columns: (1.4fr, 1fr, 1.2fr, 1.2fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header([*Statistic*], [*ESG Score*], [*Pretax ROA (%)*], [*Pretax ROE (%)*]),
    [Mean], [47.00], [1.65], [13.64],
    [Standard deviation], [21.69], [2.05], [8.42],
    [Minimum], [2.42], [−1.39], [−8.08],
    [Maximum], [92.63], [16.13], [47.66],
    [2011 (median)], [40.81], [1.28], [14.60],
    [2025 (median)], [63.76], [1.27], [12.51],
    [Median change], [+56.2%], [−0.7%], [−14.3%],
  ),
  caption: [Firm-year descriptive statistics (2011–2025, ROA/ROE winsorized)],
) <tab:desc-stats>

ESG scores climbed steadily (median 40.8 → 63.8), but cross-firm dispersion remained large throughout (annual standard deviation ≈ 18–20 points), indicating continued heterogeneity rather than convergence. Median ROA was essentially flat, dipping to about 0.96% in 2022 before recovering. Median ROE drifted modestly lower. After winsorization, the 2020 ROE shows no pandemic "crash" (median ≈ 12.6%, in line with adjacent years); the earlier apparent collapse was a single distressed firm, not a sector event.

#figure(
  table(
    columns: (0.8fr, 1.2fr, 1.3fr, 1.3fr),
    align: left,
    inset: 4pt,
    stroke: 0.5pt + luma(180),
    table.header([*Year*], [*ESG (median)*], [*ROA (median, %)*], [*ROE (median, %)*]),
    [2011], [40.81], [1.28], [14.60],
    [2012], [37.94], [1.48], [15.90],
    [2013], [36.21], [1.53], [15.50],
    [2014], [35.38], [1.51], [15.00],
    [2015], [36.18], [1.51], [15.55],
    [2016], [39.64], [1.50], [14.76],
    [2017], [42.20], [1.35], [13.83],
    [2018], [46.16], [1.24], [12.19],
    [2019], [51.36], [1.27], [12.68],
    [2020], [56.36], [1.28], [12.61],
    [2021], [57.93], [1.20], [12.73],
    [2022], [60.91], [0.96], [10.54],
    [2023], [61.88], [1.31], [12.81],
    [2024], [63.82], [1.21], [12.52],
    [2025], [63.76], [1.27], [12.51],
  ),
  caption: [Annual sector medians (N = 150 firms each year)],
) <tab:annual-medians>

#figure(
  image("outputs/banking_esg_relationship_analysis.png", width: 100%),
  caption: [Historical trends of ESG scores, pretax ROA, and pretax ROE (sector medians)],
) <fig:historical-trends>

== ESG and financial performance: panel fixed-effects results

The central finding is a null result: ESG scores have no statistically significant association with Pretax ROA or Pretax ROE once firm and year fixed effects are controlled and standard errors are clustered by firm (@tab:fe-results). All four specifications are insignificant, with within-firm $R^2$ essentially zero—that is, within-firm variation in ESG explains none of the within-firm variation in profitability.

#figure(
  table(
    columns: (1.1fr, 1.2fr, 0.9fr, 0.9fr, 0.6fr, 0.8fr, 1fr, 0.8fr),
    align: left,
    inset: 4pt,
    stroke: 0.5pt + luma(180),
    table.header(
      [*Outcome*], [*ESG term*], [*β*], [*SE*], [*t*], [*p*], [*n*], [*Within-$R^2$*],
    ),
    [Pretax ROA], [contemporaneous], [0.00105], [0.00329], [0.32], [0.750], [2,230], [≈ 0],
    [Pretax ROA], [one-year lag], [0.00361], [0.00305], [1.18], [0.237], [2,082], [≈ 0],
    [Pretax ROE], [contemporaneous], [0.00147], [0.02119], [0.07], [0.945], [2,225], [≈ 0],
    [Pretax ROE], [one-year lag], [0.01341], [0.02109], [0.64], [0.525], [2,077], [≈ 0],
  ),
  caption: [Two-way fixed-effects panel regressions (firm + year FE; SE clustered by firm)],
) <tab:fe-results>

In substantive terms, a one-point change in a bank's ESG score is associated with a change in profitability that is statistically indistinguishable from zero. The pooled firm-year correlations tell the same story: $r = 0.014$ for ESG–ROA ($n = 2,230$) and $r = 0.120$ for ESG–ROE ($n = 2,225$)—both negligible.

#figure(
  image("outputs/banking_detailed_relationship.png", width: 95%),
  caption: [Firm-year relationship between ESG and pretax profitability],
) <fig:esg-cfp-detail>

#figure(
  image("outputs/_check_fig2_esg_roa.png", width: 75%),
  caption: [Pretax ROA (%) versus ESG score (firm-year) with near-flat OLS fit],
) <fig:esg-roa-scatter>

This contrasts sharply with the strong negative correlation ($r ≈ −0.55$) reported when firms are collapsed into a single annual sector average. That approach reduces roughly 2,230 observations to 15 points and measures only the co-movement of two sector-wide trends (rising ESG, gently drifting profitability)—a spurious, trend-driven artifact rather than a firm-level relationship.

=== Heterogeneity: country groups and industry

Re-estimating the same FE model within geographic and industry groups largely reproduces the pooled null. @tab:het-country and @tab:het-industry report contemporaneous ESG coefficients; forest plots show the same contemporaneous pattern.

#set text(size: 8.5pt)
#figure(
  table(
    columns: (1.6fr, 0.7fr, 0.9fr, 0.9fr, 0.8fr, 0.8fr, 0.7fr),
    align: left,
    inset: 4pt,
    stroke: 0.5pt + luma(180),
    table.header([*Group*], [*Outcome*], [*β*], [*SE*], [*p*], [*n*], [*Firms*]),
    [Full sample], [ROA], [0.00105], [0.00329], [0.750], [2,230], [150],
    [Full sample], [ROE], [0.00147], [0.02120], [0.945], [2,225], [150],
    [Japan], [ROA], [0.00298], [0.00877], [0.734], [553], [37],
    [Japan], [ROE], [0.03576], [0.04937], [0.469], [553], [37],
    [China (incl. Hong Kong)], [ROA], [0.00783], [0.01352], [0.563], [352], [24],
    [China (incl. Hong Kong)], [ROE], [0.08102], [0.03714], [0.030], [352], [24],
    [Korea], [ROA], [0.00293], [0.00722], [0.686], [231], [16],
    [Korea], [ROE], [0.02159], [0.05844], [0.712], [231], [16],
    [Taiwan], [ROA], [0.00181], [0.00189], [0.339], [195], [13],
    [Taiwan], [ROE], [−0.02069], [0.02821], [0.464], [195], [13],
    [India], [ROA], [0.00550], [0.01840], [0.765], [195], [13],
    [India], [ROE], [−0.08920], [0.10753], [0.408], [190], [13],
    [ASEAN], [ROA], [−0.00238], [0.00397], [0.550], [419], [28],
    [ASEAN], [ROE], [−0.05578], [0.05520], [0.313], [419], [28],
    [West Asia / Middle East], [ROA], [−0.00361], [0.00585], [0.537], [285], [19],
    [West Asia / Middle East], [ROE], [−0.04189], [0.04755], [0.379], [285], [19],
  ),
  caption: [Contemporaneous ESG FE coefficients by country group],
) <tab:het-country>
#set text(size: 11pt)

#figure(
  image("outputs/banking_heterogeneity_country_forest.png", width: 95%),
  caption: [Forest plot of contemporaneous ESG FE coefficients by country group],
) <fig:het-country-forest>

#set text(size: 8.5pt)
#figure(
  table(
    columns: (1.4fr, 0.7fr, 0.9fr, 0.9fr, 0.8fr, 0.8fr, 0.7fr),
    align: left,
    inset: 4pt,
    stroke: 0.5pt + luma(180),
    table.header([*Group*], [*Outcome*], [*β*], [*SE*], [*p*], [*n*], [*Firms*]),
    [Full sample], [ROA], [0.00105], [0.00329], [0.750], [2,230], [150],
    [Full sample], [ROE], [0.00147], [0.02120], [0.945], [2,225], [150],
    [Banks], [ROA], [0.00052], [0.00191], [0.785], [1,445], [97],
    [Banks], [ROE], [0.01396], [0.02168], [0.520], [1,445], [97],
    [Insurance], [ROA], [0.00342], [0.00783], [0.663], [311], [21],
    [Insurance], [ROE], [0.01017], [0.04405], [0.818], [306], [21],
    [Other financials], [ROA], [−0.00235], [0.01517], [0.877], [474], [32],
    [Other financials], [ROE], [−0.00665], [0.05066], [0.896], [474], [32],
  ),
  caption: [Contemporaneous ESG FE coefficients by industry group],
) <tab:het-industry>
#set text(size: 11pt)

#figure(
  image("outputs/banking_heterogeneity_industry_forest.png", width: 90%),
  caption: [Forest plot of contemporaneous ESG FE coefficients by industry group],
) <fig:het-industry-forest>

Almost every subsample coefficient is statistically indistinguishable from zero, including Banks (the bulk of the sample) and Japan. No industry group shows any significant association, and outside the one exception below, no country group even approaches conventional significance (the next-smallest $p$-value in the heterogeneity results is 0.15, for lagged ESG → ROE in Japan; all other contemporaneous $p$-values exceed 0.31).

*Secondary finding: a positive contemporaneous ESG–ROE association in China (incl. Hong Kong).* The single exception to the null is the Greater China subsample (24 firms, 352 firm-years), where a one-point increase in a firm's ESG score is associated with a same-year increase of roughly 0.08 percentage points in pretax ROE ($β ≈ 0.081$, $"SE" ≈ 0.037$, $p ≈ 0.030$)—equivalently, a 10-point ESG improvement corresponds to about +0.8 pp ROE. It is the only positive market-level signal in the sample and is consistent with the view that ESG performance carries more financial relevance in Chinese and Hong Kong-listed financials—for example through state-aligned policy incentives, green-finance mandates, or investor attention—than elsewhere in Asia over this period.

Several features nonetheless mark this as a suggestive rather than a confirmed result. The association appears only for ROE, not ROA ($p ≈ 0.56$), in the same group; it does not survive a one-year lag ($p ≈ 0.45$), so there is no evidence that ESG improvements precede the profitability gains; the specification's within-$R^2$ is negative (−0.14, i.e. no explanatory gain); and with roughly 40 subsample regressions estimated, about two significant results at the 5% level would be expected by chance alone. It is therefore reported as an exploratory, hypothesis-generating finding—a candidate for targeted future work on Greater China financials—rather than as a confirmed regional "ESG pays" effect.

== Machine-learning models: no out-of-sample predictive power

Evaluated honestly out-of-sample (GroupKFold by firm), none of the three models can predict either financial metric from ESG (@tab:ml-performance). Every test $R^2$ is negative, meaning the models predict worse than simply using the mean. The large gap between training $R^2$ (≈ 0.08–0.17) and test $R^2$ confirms that any in-sample fit is overfitting. This directly reverses earlier claims of near-perfect accuracy ($R^2 ≈ 1.0$), which were produced by evaluating models on their own training data.

#figure(
  table(
    columns: (0.9fr, 1.3fr, 1fr, 1fr, 1.1fr, 1fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header(
      [*Outcome*], [*Model*], [*Test $R^2$*], [*Train $R^2$*], [*Test RMSE*], [*Test MAE*],
    ),
    [ROA], [XGBoost], [−0.088], [0.140], [2.244], [1.312],
    [ROA], [Random Forest], [−0.123], [0.172], [2.279], [1.306],
    [ROA], [Decision Tree], [−0.219], [0.119], [2.339], [1.328],
    [ROE], [XGBoost], [−0.020], [0.114], [9.118], [6.792],
    [ROE], [Random Forest], [−0.006], [0.125], [9.058], [6.725],
    [ROE], [Decision Tree], [−0.019], [0.078], [9.115], [6.782],
  ),
  caption: [Out-of-sample ML performance (GroupKFold by firm)],
) <tab:ml-performance>

== Illustrative forecast (2026–2030)

Using a linear-trend model on the annual median series, ESG is projected to continue rising while profitability drifts modestly lower (@tab:forecast). These are illustrative sector-trend extrapolations with wide prediction intervals, based on only 15 annual points; they describe the continuation of past trends, not a causal consequence of ESG integration, and should not be read as an ESG-driven "steady state."

#figure(
  table(
    columns: (0.7fr, 1.5fr, 1.6fr, 1.6fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header(
      [*Year*], [*ESG (95% PI)*], [*Pretax ROA %, (95% PI)*], [*Pretax ROE %, (95% PI)*],
    ),
    [2026], [67.4 (57.8–77.0)], [1.14 (0.84–1.45)], [11.29 (9.03–13.56)],
    [2027], [69.7 (59.9–79.6)], [1.12 (0.81–1.43)], [11.01 (8.69–13.33)],
    [2028], [72.1 (62.0–82.2)], [1.10 (0.78–1.41)], [10.72 (8.34–13.10)],
    [2029], [74.4 (64.0–84.8)], [1.07 (0.75–1.40)], [10.43 (8.00–12.87)],
    [2030], [76.7 (66.1–87.4)], [1.05 (0.71–1.38)], [10.15 (7.64–12.65)],
  ),
  caption: [Linear-trend forecast with 95% prediction intervals],
) <tab:forecast>

#figure(
  image("outputs/banking_forecast_2026_2030.png", width: 100%),
  caption: [Illustrative linear-trend forecast of pretax ROA and ROE (2026–2030)],
) <fig:forecast>

== Rolling correlations: stably weak, no turning point

Recomputed on firm-year data using observed values only, the rolling 5-year correlations are consistently weak throughout the period (@tab:rolling-corr): ESG–ROA stays close to zero and ESG–ROE remains mildly positive but small. There is no swing from strong negative to strong positive values. The earlier "cost-heavy negative phase → value-creation turning point" narrative was an artifact of correlating only 15 sector-average points and of extending the rolling windows into forecasted (rather than observed) values, which mechanically produced near-perfect correlations.

#figure(
  image("outputs/_check_fig6_rolling.png", width: 90%),
  caption: [Rolling 5-year correlations (observed firm-year data only)],
) <fig:rolling-corr>

#figure(
  table(
    columns: (1.2fr, 1.2fr, 1.2fr),
    align: left,
    inset: 5pt,
    stroke: 0.5pt + luma(180),
    table.header([*Window end year*], [*ESG–ROA*], [*ESG–ROE*]),
    [2015], [0.018], [0.138],
    [2016], [0.011], [0.151],
    [2017], [0.021], [0.172],
    [2018], [0.021], [0.171],
    [2019], [0.022], [0.174],
    [2020], [0.038], [0.196],
    [2021], [0.054], [0.204],
    [2022], [0.040], [0.173],
    [2023], [0.042], [0.180],
    [2024], [0.066], [0.213],
    [2025], [0.075], [0.221],
  ),
  caption: [Rolling 5-year correlations (observed firm-year data only)],
) <tab:rolling-corr>

== Summary of findings

Across every method—panel fixed-effects regression, country- and industry-group subsample FE, firm-year correlations, out-of-sample machine learning, and rolling-window analysis—the evidence points the same way: once firm heterogeneity, common time shocks, and outliers are properly handled, there is no robust short-run within-firm association between ESG scores and pretax profitability for Asian BFSI firms in this sample. Country and industry splits largely confirm the pooled null (Banks and Japan included); the one secondary finding—a positive contemporaneous ESG → ROE association in China (incl. Hong Kong), reported above as exploratory and hypothesis-generating—does not overturn that pattern. The strong relationships and near-perfect predictions reported under earlier sector-average methodology were artifacts of aggregation, in-sample evaluation, and a single distressed-firm outlier.

= Conclusion and Discussion

This research examines the relationship between ESG performance and financial performance in the Asian BFSI sector over 2011–2025 using a firm-level panel of approximately 2,250 firm-year observations. Contrary to designs that report a short-term ESG–performance trade-off from aggregated series, the analysis finds no statistically significant association between ESG scores and either Pretax ROA or Pretax ROE in two-way fixed-effects regressions with firm-clustered standard errors. Within-firm explanatory power is near zero; firm-year correlations are negligible; and out-of-sample machine-learning models return negative test $R^2$, indicating no exploitable ESG–CFP signal.

Heterogeneity checks reinforce the pooled null for Banks, Japan, and nearly every other country and industry group examined. The sole exception—a positive contemporaneous ESG–ROE association in China (including Hong Kong)—is reported as exploratory: it does not appear for ROA, does not survive a one-year lag, adds no within-firm explanatory power, and could arise by chance among many subsample tests. It is a candidate for targeted future work, not a confirmed regional "ESG pays" result.

The substantive implication is measured: over this period and sample, composite ESG scores appear to be neither a meaningful short-run driver nor a meaningful drag on accounting profitability for Asian BFSI firms. Forecasts reported here are illustrative sector-trend extrapolations, and the earlier "value-creation turning point" narrative is not supported once rolling correlations are computed on observed firm-year data. Conclusions about ESG and financial performance are highly sensitive to methodology; firm-level panel methods with proper out-of-sample validation are essential to avoid spurious findings.

= Policy and Managerial Implications

For financial institutions, the central message is that, over this period and sample, higher ESG scores are associated with neither a short-run profitability penalty nor a short-run profitability premium. Institutions should neither expect ESG investment to pay for itself quickly through higher ROA or ROE, nor treat it as a drag to be minimised on those grounds. ESG decisions are better justified on regulatory compliance, risk management, funding access, and stakeholder expectations, and monitored through leading and non-financial indicators rather than headline profitability alone. Given wide dispersion of ESG performance across firms, the quality and materiality of implementation matter more than the level of the composite score.

For investors, the evidence cautions against assuming a direct, near-term link between ESG ratings and accounting returns in this sector once firm and time effects are controlled. Heterogeneity results further warn against treating Asia as a single ESG–CFP regime; any China/Hong Kong signal should be treated as provisional pending pillar-level and identification-focused research. Policymakers and regulators can most usefully improve the comparability and reliability of ESG disclosure so that longer-run relationships can be measured accurately, and should rest policy evidence on firm-level, appropriately controlled analysis rather than on aggregated correlations.

= Limitations and Future Directions

This research has several limitations. First, the analysis relies on composite Refinitiv ESG scores and does not decompose them into Environmental, Social, and Governance pillars. Second, firm-and-year fixed effects control for time-invariant firm traits and common annual shocks but do not establish causality; residual endogeneity and time-varying omitted variables may remain. Third, the illustrative forecast rests on only 15 annual points and carries wide prediction intervals. Fourth, the sample is confined to Asian BFSI firms, which may limit generalisability. The China/Hong Kong ESG–ROE association, while noteworthy, is exploratory and requires stronger designs before it can guide policy or portfolio construction.

Future work could disaggregate ESG into pillars; apply instrumental-variable or difference-in-differences designs around disclosure or green-finance mandates (especially in Greater China); add time-varying controls such as firm size, capital structure, and regulatory environment; examine risk-adjusted performance rather than return ratios alone; and extend the sample to other regions and to private or smaller financial firms.

#bibliography(
  "references.bib",
  style: "apa",
  title: "References",
  full: true,
)
