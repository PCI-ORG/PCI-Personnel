_Last updated on September 10, 2024._

## 1. What is the PCI-Personnel?

The PCI-Personnel is an algorithm for tracking the prominence of different personnel around a political leader. In a first use case, we develop the PCI-Personnel for top Chinese politicians around Chinese President Xi Jinping. Both the Chinese and English names of the politicians can be found in the config folder. 

## 2. Methodology

The PCI-Personnel algorithm consists of the following five steps:

1. Data extraction: It takes input data from the full text of the People’s Daily, the Chinese Communist Party (CCP)'s most prominent mouthpiece.

2. Data preparation: We first compile a list of persons of interest (POIs), which in the current version includes 28 top Chinese politicians formerly or currently serving in the CCP’s Central Committee. For each POI, the algorithm selects news articles that involve both the POI and Xi (e.g., when they appear at a same public event).

3. Data analysis: We employ large language models (LLMs) to assign a score on a scale of -5 to +5 for the relationship between the POI and Xi as perceived by the newspaper. For each POI, the LLM analysis is implemented at the article level; that is, the relationship between any POI and Xi could fluctuate from article to article, or from time to time.

4. Modeling: For each POI, we aggregate the article-level relationship scores into a (POI-level) index over time. Specifically, the index for each POI starts with 0 on January 1, 2001. On each day, we aggregate the scores across all relevant articles and add the sum to the index. However, if a POI doesn’t receive coverage on any day, their index value decays by 1% compared to the day before. In other words, without any further converge, an index, positive or negative, would converge to 0 in the long run. The idea of the decay assumption is that, for a politician who is highly placed and used to being positively and regularly covered by the party mouthpiece, no press essentially means bad press. On the other hand, when a politician previously covered negatively starts to retreat from the spotlight, it might suggest an improvement of status.

5. Visualization: We plot and deploy the numerical indices for all POIs and continue to update the results as new data continues to flow in.

The visualization of the results can be found here: https://pci-org.github.io/PCI-Personnel/.

## Acknowledgement

This project is a collaboration between PCI and Gear Factory, a company specialized in deploying artificial intelligence solutions.