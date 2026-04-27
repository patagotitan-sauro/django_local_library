
from django.http import HttpResponse, HttpResponseRedirect # method import

from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Choice, Question

#from django.shortcuts import render

# Create your views here.
def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    context = {"latest_question_list": latest_question_list}
    return HttpResponse(template.render(context, request))
    #return HttpResponse("You're at the polls index. 7491a32c 26e92deb ")

def detail(request, question_id):
    return HttpResponse(f"You are looking to the question {question_id}s.")

def owner(request) -> HttpResponse:
    response = HttpResponse()
    response.write("Hello, world. 26e92deb.")
    return response

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})
    """
    response = "You're looking at the results of question %s. 26e92deb "
    return HttpResponse(response % question_id)
    """
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
         # Redisplay the question voting form.
         return render(
             request, "polls/detail.html",
             {
                 "question": question,
                 "error_message": "You didn't select a choice.",
                 }, )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

    #return HttpResponse("You're voting on question %s. 26e92deb" % question_id)




