-- Metadata -- 

Select
	'Lepmon' As project_identifier,
	p2.name As project_title,
	Concat(p2.description, '|',
		p1.name, '|', p1.description, '|',
		p0.name, '|', p0.description) As project_description,
    GROUP_CONCAT(
        DISTINCT CONCAT_WS(' ', allu.first_name, allu.last_name)
        ORDER BY allu.last_name, allu.first_name
        SEPARATOR '; '
    ) AS project_contributor,
	Min(r.lon) as min_lon,
	Min(r.lat) as min_lat,
	Max(r.lon) as max_lon,
	Max(r.lat) as max_lat,
	Min(m.`created`) As min_time,
	Max(m.`created`) As max_time,
	'Lepidoptera' As project_taxa
From annot8_api_media m
    Left Join annot8_api_run r On m.run_id = r.id
    Left Join annot8_api_trap t On t.id = r.trap_id
    Left Join annot8_api_project p0 On p0.id = t.project_id
    Left Join annot8_api_project p1 On p1.id = p0.parent_project_id
    Left Join annot8_api_project p2 On p2.id = p1.parent_project_id
	LEFT JOIN annot8_api_project_admins paa ON paa.project_id IN (p0.id, p1.id, p2.id)
	LEFT JOIN auth_user allu ON allu.id = paa.user_id
Where r.id = 2533; -- in (8193);

-- Deployment --

Select 
	r.locality_id as deployment_id,
	r.lon As longitude,
	r.lat As latitude,
    Concat(t.locality_desc, ', ', t.city) As locationName,
	JSON_UNQUOTE(JSON_EXTRACT(mt.data, '$.deploymentStart')) AS deployment_start,
    JSON_UNQUOTE(JSON_EXTRACT(mt.data, '$.deploymentEnd')) AS deployment_end,
	t.serial_number As cameraID,
    JSON_UNQUOTE(JSON_EXTRACT(mt_c.data, '$.cameraModel')) AS cameraModel,
    JSON_UNQUOTE(JSON_EXTRACT(mt_c.data, '$.cameraVersion')) AS cameraVersion,
    JSON_UNQUOTE(JSON_EXTRACT(mt_c.data, '$.detectionDistance')) AS detectionDistance,
    JSON_UNQUOTE(JSON_EXTRACT(mt_b.data, '$.baitUse')) AS baitUse,
    JSON_UNQUOTE(JSON_EXTRACT(mt_b.data, '$.baitType')) AS baitType,
    JSON_UNQUOTE(JSON_EXTRACT(mt_c.data, '$.firmwareVersion')) AS firmwareVersion,
    JSON_UNQUOTE(JSON_EXTRACT(mt_c.data, '$.firmwareDate')) AS firmwareDate
From annot8_api_run r
    Left Join annot8_api_trap t On t.id = r.trap_id
    Left Join annot8_api_trapmetadata mt On mt.trap_id = r.trap_id and mt.source = 'deploymentStart'
    Left Join annot8_api_trapmetadata mt_c On mt_c.trap_id = r.trap_id and mt_c.source = 'camera'
    Left Join annot8_api_trapmetadata mt_b On mt_b.trap_id = r.trap_id and mt_b.source = 'bait'
Where r.id = 2533; -- in (8193);


-- Media --

Select 
	m.id As media_id,
	r.locality_id As deploymentID,
	'automatic interval exposure' As 'captureMethod',
	m.created As timestamp,
	Concat('https://lepmon.de/annot8/media/', Cast(m.id As Char)) As filePath,
	'Y' As filePublic,
	m.file_name As fileName,
	'image' As fileMediatype
From annot8_api_media m
    Left Join annot8_api_run r On m.run_id = r.id
    Left Join annot8_api_trap t On r.trap_id = t.id
    Left Join annot8_api_project p On t.project_id = p.id
Where r.id = 2533 And meta=0;

-- Detections --

SELECT r.locality_id As deploymentID,
	Min(m.id) AS media_id,
	Min(m.`created`) As eventStart,
	Max(m.`created`) As eventEnd,
	'media' As detectionLevel,
	tp.name AS scientificName,
    tp.rank AS taxonRank,
    Count(bb.describableobject_ptr_id) As count,
	bb.track_id As individualID,
	bb.total_x AS bboxX,
    bb.total_y AS bboxY,
    bb.total_width AS bboxWidth,
    bb.total_height AS bboxHeight,
    Concat('https://lepmon.de/annot8/iiif/',
    	Cast(Min(m.id) As Char), '/',
    	Cast(bb.total_x As Char), ',',
    	Cast(bb.total_y As Char), ',',
    	Cast(bb.total_width As Char), ',',
    	Cast(bb.total_height As Char),
    	'/max/0/default.jpg') As bboxURL,
    p.score As classificationProbability,
    CONCAT(ai.model_name, ai.model_version) AS modelID,
    IF(bb.pipeline_generated=1, 'machine', 'human') As classificationMethod,
    p.created As classificationTimestamp
From annot8_api_media m
	INNER Join annot8.annot8_api_run r ON m.run_id = r.id
	Left Join annot8.annot8_api_boundingbox bb ON m.id = bb.described_file_id
	Left Join annot8.annot8_api_prediction p ON bb.track_id = p.track_id
	Left Join annot8.annot8_api_aimodel ai On p.model_id = ai.id
	Left Join annot8.annot8_api_taxa tp ON p.top_1_taxon_id = tp.id
Where m.run_id=2533
	And  bb.describableobject_ptr_id is not null And tp.id is not null
Group By bb.track_id;


-- Model --

Select
	Concat(ai.model_name, model_version) As modelID,
	ai.model_name As modelName,
	ai.model_version As modelVersion,
	ai.model_description As modelDescription,
	ai.model_path_repository As modelPathRepository,
	ai.publication_date As publicationDate,
	ai.model_task As modelTask
From annot8_api_media m
	Left Join annot8.annot8_api_boundingbox bb ON m.id = bb.described_file_id
	Left Join annot8.annot8_api_prediction p ON bb.track_id = p.track_id
	Left Join annot8.annot8_api_aimodel ai On p.model_id = ai.id
Where m.run_id=2533 And ai.model_name is not NULL
Group By ai.id;
