### 规则处理方案

1、先将规则进行词法分析，将规则分割为规则列表

2、将规则列表按规则类型进行分类组合

```python
// 例如 .status@text&&[property=\"og:novel:category\"]@content##小说|.*：|\\s.*
[{'type': <RuleType.GetAndInner: 13>, 'tokens': ['{{', '$.latest_chapter_title', '}}', '·', '{{', "java.timeFormat(java.getString('$.update_time')*1000)", '}}']}]
```

3、根据规则类型进行预处理
