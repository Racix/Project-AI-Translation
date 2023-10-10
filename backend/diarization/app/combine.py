import json
import sys

# if len(sys.argv) != 2:
#     print("Usage: python3 NeMo-SpeakerDiarization.py <filename>")
#     sys.exit(1)

# filename = sys.argv[1]
# print(f"Processing file: {filename}")

# data_dir = "/tf/Project-AI-Translation/diarization/data/"
# result_dir = "/tf/Project-AI-Translation/diarization/result/"

# def parse_rttm(rttm_file):
#     segments = []
#     with open(rttm_file, 'r') as f:
#         for line in f:
#             parts = line.strip().split()
#             start, duration = float(parts[3]), float(parts[4])
#             text = ' '.join(parts[10:]) if len(parts) > 10 else None
#             speaker = parts[7] if "speaker" in parts[7] else None
#             print(speaker)
#             segments.append({"start": start, "duration": duration, "text": text, "speaker": speaker})
#     print(segments)
#     return segments
    
# def segments_overlap(seg1, seg2):
#     """Check if two segments overlap."""
#     return seg1["start"] < seg2["start"] + seg2["duration"] and seg1["start"] + seg1["duration"] > seg2["start"]

# def isInnerSegment(trans_seg, dia_seg):
#     return trans_seg["start"] >= dia_seg["start"] and trans_seg["start"] + trans_seg["duration"] <= dia_seg["start"] + dia_seg["duration"]
    
# def match_and_write_to_json(transcript_file, diarization_file, output_file):
#     transcript_segments = parse_rttm(transcript_file)
#     diarization_segments = parse_rttm(diarization_file)
    
#     combined_data = []
#     dia_iter = iter(diarization_segments)
#     dia_seg = next(dia_iter)
#     unknown_speaker = False
#     for trans_seg in transcript_segments:
#         print("start on", trans_seg["start"], dia_seg["start"])
#         while not segments_overlap(dia_seg, trans_seg):
            
#             if dia_seg["start"] < trans_seg["start"]:
#                 try:
#                     dia_seg = next(dia_iter)
#                 except StopIteration:
#                     dia_seg["speaker"] = "Unknown"
#                     appendData(combined_data, trans_seg, "Unknown")
#                     unknown_speaker = True
#                     break
#             if trans_seg["start"] < dia_seg["start"]:
#                 appendData(combined_data, trans_seg, "Unknown")
#                 unknown_speaker = True
#                 break
#         if unknown_speaker:
#             unknown_speaker = True
#             continue
            
#         if isInnerSegment(trans_seg, dia_seg): 
#             appendData(combined_data, trans_seg, dia_seg["speaker"])
#             continue
            
#         # if this reaches, there might be a clash of who speaks
#         considered_dia_segments = []
#         while dia_seg["start"] < trans_seg["start"] + trans_seg["duration"]:
#             considered_dia_segments.append(dia_seg)
#             try:
#                 dia_seg = next(dia_iter)
#             except StopIteration:
#                 break

#         segment_consideration_percent = []
#         for segs in considered_dia_segments:
#             comb_seg_start = max(segs["start"], trans_seg["start"])
#             comb_seg_stop = min(segs["start"] + segs["duration"], trans_seg["start"] + trans_seg["duration"])
#             segment_consideration_percent.append((comb_seg_stop - comb_seg_start) / trans_seg["duration"])
#         print("UNSURE: PRINT %:", segment_consideration_percent, considered_dia_segments)
#         max_index = segment_consideration_percent.index(max(segment_consideration_percent))
#         considered_dia_segments[max_index]["speaker"] = considered_dia_segments[max_index]["speaker"] + " " + str(segment_consideration_percent[max_index])

#         appendData(combined_data, trans_seg, considered_dia_segments[max_index]["speaker"])

#     # combined_data = []
#     # for dia_seg in diarization_segments:
#     #     for trans_seg in transcript_segments:
#     #         if segments_overlap(dia_seg, trans_seg):
#     #             print("TÄSTS: ", trans_seg, "!!!", trans_seg["text"])
#     #             combined_data.append({
#     #                 "text": trans_seg["text"],
#     #                 "start": dia_seg["start"],
#     #                 "duration": dia_seg["duration"],
#     #                 "speaker": dia_seg["speaker"]
#     #             })
#     #             break

#     with open(output_file, 'w') as f:
#         json.dump(combined_data, f, indent=4)

def appendData(combined_data, trans_seg, speaker):
    combined_data.append({
        "text": trans_seg["text"],
        "start": trans_seg["start"],
        "duration": trans_seg["duration"],
        "speaker": speaker
    })

def segments_overlap(seg1, seg2):
    """Check if two segments overlap."""
    return seg1["start"] < seg2["start"] + seg2["duration"] and seg1["start"] + seg1["duration"] > seg2["start"]


def align_segments_with_overlap_info(transcript_segments, diarization_segments):
    combined_data = []
    
    for trans_seg in transcript_segments:
        overlapping_dia_segments = [
            dia_seg for dia_seg in diarization_segments 
            if segments_overlap(trans_seg, dia_seg)
        ]
        
        if not overlapping_dia_segments:
            combined_data.append({
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
            
            combined_data.append({
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
            
            combined_data.append({
                "text": trans_seg["text"],
                "start": trans_seg["start"],
                "duration": trans_seg["duration"],
                "speaker": chosen_dia_seg["speaker"],
                "overlap_percentage": overlap_percentage
            })

    return combined_data

# Adjusting the parse_rttm function to read from a file
def parse_rttm_from_file(file_path):
    name = file_path.split("/")[-1].split(".")[0]
    rttm_path = f"/diarization/config/oracle_vad/pred_rttms/{name}.rttm"
    segments = []
    with open(rttm_path, 'r', encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            start, duration = float(parts[3]), float(parts[4])
            text = ' '.join(parts[10:]) if len(parts) > 10 else None
            speaker = parts[7] if "speaker" in parts[7] else None
            segments.append({"start": start, "duration": duration, "text": text, "speaker": speaker})
    return segments

# Parse the RTTM files


# Align the segments and get the combined data



# # Paths to the RTTM files and output JSON file
# transcript_file = data_dir + filename + ".rttm"
# diarization_file = data_dir + "oracle_vad/pred_rttms/" + filename + ".rttm"
# output_file = result_dir + filename + ".json"

# transcript_segments_file = parse_rttm_from_file(transcript_file)
# diarization_segments_file = parse_rttm_from_file(diarization_file)

# combined_data_file = align_segments_with_overlap_info(transcript_segments_file, diarization_segments_file)

# # Save the combined data to a JSON file

# with open(output_file, 'w', encoding="utf-8") as f:
#     json.dump(combined_data_file, f, indent=4)



