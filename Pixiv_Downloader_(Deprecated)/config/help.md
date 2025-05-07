extractor.skip:
If true, skips files already downloaded but continues scanning for older works. If set to "abort:N", stops scanning after N consecutive already-downloaded files. Default is true.

extractor.sleep:
Number of seconds to wait between requests. Helps avoid rate-limiting. Default is 0.

extractor.pixiv.base-directory:
Root folder for saving downloaded files.

extractor.pixiv.directory:
Subdirectory structure for organizing downloads. Uses placeholders like {user[id]}, {user[account]}, etc.

extractor.pixiv.filename:
Naming pattern for downloaded files. Placeholders like {id}, {num}, {extension} are replaced with actual values.

extractor.pixiv.refresh-token:
OAuth refresh token for Pixiv. Needed for accessing restricted content.

extractor.pixiv.metadata:
If true, downloads a metadata file for each work.

extractor.pixiv.tags:
List of tags to filter works. Only works containing these tags are downloaded.

extractor.pixiv.skip:
Overrides the global skip setting for Pixiv. Can be true, false, or "abort:N".

extractor.pixiv.postprocessors:
List of postprocessors to run after download.

extractor.pixiv.ugoira-conv:
If set, converts ugoira (Pixiv animated zip) to gif or webm. Example: "webm" or "gif".

extractor.pixiv.ugoira-fps:
Frames per second for ugoira conversion. Default is 30.

extractor.pixiv.ugoira-quality:
Quality setting for gif/webm conversion.

extractor.pixiv.user-id:
Pixiv user ID to restrict downloads to a specific user.

extractor.pixiv.max-pages:
Maximum number of pages to scan for works.

extractor.pixiv.bookmarks:
If true, downloads bookmarked works instead of user posts.

extractor.pixiv.illusts:
If true, downloads illustrations only (not manga or novels).

extractor.pixiv.manga:
If true, downloads manga only.

extractor.pixiv.novels:
If true, downloads novels only.

extractor.pixiv.r18:
If true, includes R-18 (adult) works.

extractor.pixiv.exclude:
List of tags to exclude from download.

extractor.pixiv.date-min and extractor.pixiv.date-max:
Limits downloads to works posted after/before a certain date (YYYY-MM-DD).

extractor.pixiv.search:
Custom search query for Pixiv works.

postprocessor.metadata-pixiv.name:
Name of the postprocessor module.

postprocessor.metadata-pixiv.mode:
Format of the metadata output, e.g., "json".

postprocessor.metadata-pixiv.event:
When to run the postprocessor. "post" means after download.

postprocessor.metadata-pixiv.filename:
Naming pattern for the metadata file.

output.skip:
Whether to skip files based on output settings. Usually false.

For more options and details, see the gallery-dl documentation: https://gdl-org.github.io/docs/configuration.html