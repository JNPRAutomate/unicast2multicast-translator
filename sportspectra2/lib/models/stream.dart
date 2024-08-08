class StreamModel {
  final int? id;
  final String channelId;
  final String title;
  final String description;
  final String category;
  final String status;
  final String image;
  final String? videoUrl;
  final int viewers;
  final String organization;
  bool liked;
  int totalLikes;
  final String? sourceIp;
  final String? groupIp;
  final String? udpPort;
  final String? amtRelay;

  StreamModel({
    this.id,
    required this.channelId,
    required this.title,
    required this.description,
    required this.category,
    required this.status,
    required this.image,
    required this.viewers,
    required this.organization,
    this.videoUrl,
    this.liked = false,
    this.totalLikes = 0,
    this.sourceIp,
    this.groupIp,
    this.udpPort,
    this.amtRelay,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'channelId': channelId,
      'title': title,
      'description': description,
      'category': category,
      'status': status,
      'image': image,
      'viewers': viewers,
      'organization': organization,
      'videoUrl': videoUrl,
      'liked': liked ? 1 : 0,
      'totalLikes': totalLikes,
      'sourceIp': sourceIp,
      'groupIp': groupIp,
      'udpPort': udpPort,
      'amtRelay': amtRelay,
    };
  }

  factory StreamModel.fromJson(Map<String, dynamic> json) {
    return StreamModel(
      id: json['id'],
      channelId: json['channelId'],
      title: json['title'],
      description: json['description'],
      category: json['category'],
      status: json['status'],
      image: json['image'],
      viewers: json['viewers'],
      organization: json['organization'],
      videoUrl: json['videoUrl'],
      liked: json['liked'] == 1,
      totalLikes: json['totalLikes'],
      sourceIp: json['source_ip'],
      groupIp: json['groupIp'],
      udpPort: json['udpPort'],
      amtRelay: json['amtRelay'],
    );
  }
}
