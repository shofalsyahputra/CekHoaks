class ExplainingTerm {
  final String term;
  final String direction;
  final double score;
  final double impactPercent;

  ExplainingTerm({
    required this.term,
    required this.direction,
    required this.score,
    required this.impactPercent,
  });

  factory ExplainingTerm.fromJson(Map<String, dynamic> json) {
    return ExplainingTerm(
      term: json['term'] ?? '',
      direction: json['direction'] ?? 'HOAKS',
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      impactPercent: (json['impact_percent'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'term': term,
    'direction': direction,
    'score': score,
    'impact_percent': impactPercent,
  };
}

class ClassificationResult {
  final String logId;
  final String title;
  final String contentPreview;
  final String predictedLabel;
  final double hoaxProbability;
  final double factProbability;
  final double hoaxPercentage;
  final double factPercentage;
  final double confidencePercent;
  final String riskLevel;
  final List<ExplainingTerm> topTerms;
  final String sourceType;
  final String evaluatedAt;

  ClassificationResult({
    required this.logId,
    required this.title,
    required this.contentPreview,
    required this.predictedLabel,
    required this.hoaxProbability,
    required this.factProbability,
    required this.hoaxPercentage,
    required this.factPercentage,
    required this.confidencePercent,
    required this.riskLevel,
    required this.topTerms,
    required this.sourceType,
    required this.evaluatedAt,
  });

  bool get isHoax => predictedLabel == 'HOAKS';

  factory ClassificationResult.fromJson(Map<String, dynamic> json) {
    final exp = json['explanation'] as Map<String, dynamic>?;
    final termsList = (exp?['top_terms'] as List<dynamic>?)
            ?.map((e) => ExplainingTerm.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    return ClassificationResult(
      logId: json['log_id'] ?? '',
      title: json['title'] ?? '',
      contentPreview: json['content_preview'] ?? '',
      predictedLabel: json['predicted_label'] ?? 'HOAKS',
      hoaxProbability: (json['hoax_probability'] as num?)?.toDouble() ?? 0.0,
      factProbability: (json['fact_probability'] as num?)?.toDouble() ?? 0.0,
      hoaxPercentage: (json['hoax_percentage'] as num?)?.toDouble() ?? 0.0,
      factPercentage: (json['fact_percentage'] as num?)?.toDouble() ?? 0.0,
      confidencePercent: (json['confidence_percent'] as num?)?.toDouble() ?? 0.0,
      riskLevel: json['risk_level'] ?? '',
      topTerms: termsList,
      sourceType: json['source_type'] ?? 'text',
      evaluatedAt: json['evaluated_at'] ?? DateTime.now().toString(),
    );
  }

  Map<String, dynamic> toMap() => {
    'log_id': logId,
    'title': title,
    'content_preview': contentPreview,
    'predicted_label': predictedLabel,
    'hoax_probability': hoaxProbability,
    'fact_probability': factProbability,
    'hoax_percentage': hoaxPercentage,
    'fact_percentage': factPercentage,
    'confidence_percent': confidencePercent,
    'risk_level': riskLevel,
    'source_type': sourceType,
    'evaluated_at': evaluatedAt,
  };
}

