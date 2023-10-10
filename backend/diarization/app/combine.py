import os

def segments_overlap(seg1: list, seg2: list) -> bool:
    """Check if two segments overlap."""
    return seg1["start"] < seg2["start"] + seg2["duration"] and seg1["start"] + seg1["duration"] > seg2["start"]


def align_segments_with_overlap_info(transcript_segments: dict, diarization_segments: dict) -> dict:
    combined_segments = []
    
    for trans_seg in transcript_segments:
        overlapping_dia_segments = [
            dia_seg for dia_seg in diarization_segments 
            if segments_overlap(trans_seg, dia_seg)
        ]
        
        if not overlapping_dia_segments:
            combined_segments.append({
                "text": trans_seg["text"],
                "start": trans_seg["start"],
                "duration": trans_seg["duration"],
                "speaker": "Unknown",
                "overlap_percentage": 0
            })
            continue
        
        if len(overlapping_dia_segments) == 1:
            dia_seg = overlapping_dia_segments[0]
            overlap_start = max(trans_seg["start"], dia_seg["start"])
            overlap_end = min(trans_seg["start"] + trans_seg["duration"], dia_seg["start"] + dia_seg["duration"])
            overlap_duration = overlap_end - overlap_start
            
            overlap_percentage = (overlap_duration / trans_seg["duration"]) * 100
            
            combined_segments.append({
                "text": trans_seg["text"],
                "start": trans_seg["start"],
                "duration": trans_seg["duration"],
                "speaker": dia_seg["speaker"],
                "overlap_percentage": overlap_percentage
            })
        else:
            # If there are multiple overlapping segments, choose the one with the maximum overlap
            overlap_duration = [
                min(seg["start"] + seg["duration"], trans_seg["start"] + trans_seg["duration"]) - 
                max(seg["start"], trans_seg["start"]) 
                for seg in overlapping_dia_segments
            ]
            
            max_index = overlap_duration.index(max(overlap_duration))
            chosen_dia_seg = overlapping_dia_segments[max_index]
            overlap_percentage = (overlap_duration[max_index] / trans_seg["duration"]) * 100
            
            combined_segments.append({
                "text": trans_seg["text"],
                "start": trans_seg["start"],
                "duration": trans_seg["duration"],
                "speaker": chosen_dia_seg["speaker"],
                "overlap_percentage": overlap_percentage
            })

    return combined_segments

# Adjusting the parse_rttm function to read from a file
def parse_rttm_from_file(file_path: str) -> dict:
    file_name, _ = os.path.splitext(os.path.basename(file_path))
    rttm_path = f"/diarization/config/oracle_vad/pred_rttms/{file_name}.rttm"
    segments = []
    with open(rttm_path, 'r', encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            start, duration = float(parts[3]), float(parts[4])
            text = ' '.join(parts[10:]) if len(parts) > 10 else None
            speaker = parts[7] if "speaker" in parts[7] else None
            segments.append({"start": start, "duration": duration, "text": text, "speaker": speaker})
    return segments

