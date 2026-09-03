"""Render all source entries deterministically, without any model calls."""
from __future__ import annotations


def field(value: object) -> str:
    return "未提供" if value is None or value == "" else str(value)


def render_report(report: dict) -> str:
    counts = report["counts"]
    trend = report["source_status"]["trendradar"]
    lines = [f'# AI 日报｜{report["report_date"]}', '',
             f'数据生成时间：{report["generated_at"]}（北京时间）', '',
             f'AI HOT：{counts["aihot_published"]} 条；TrendRadar：{counts["trendradar_published"]} 条 AI 相关热点。',
             f'实际采集快照：{trend["snapshot_count"]} 个；平台：{trend["platform_count"]} 个。', '',
             '以下为两处信息源的完整收录，不代表已经逐条独立核实。']
    if "trendradar_incomplete_slots" in report["warnings"]:
        lines += ['', '采集说明：历史时段未齐；当前来源可用性见下方状态，不将缺少的历史快照伪装为已采集。单次采集不能据此判断热度升降。']
    lines += ['', f'来源状态：AI HOT={report["source_status"]["aihot"]["status"]}；TrendRadar={trend["status"]}。',
              '', '## AI HOT 完整资讯', '']
    for item in report["aihot_items"]:
        lines += [f'### {item["ref"]}｜{item["title"]}', '', field(item["summary"]), '',
                  f'来源：{field(item["source"])}；发布时间：{field(item["published_at"])}', '',
                  f'原文：{field(item["url"])}', f'收录页：{field(item["permalink"])}', '']
    lines += ['## TrendRadar 完整 AI 热点', '']
    for item in report["trendradar_items"]:
        lines += [f'### {item["ref"]}｜{item["title"]}', '',
                  f'平台：{item["platform"]}；榜单排名：{item["rank"]}；实际出现快照数：{item["crawl_count"]}。', '',
                  f'链接：{field(item["url"])}', '']
    lines += [f'核对：AI HOT {len(report["aihot_items"])} 条；TrendRadar {len(report["trendradar_items"])} 条。', '']
    return '\n'.join(lines)
